module  X_stack (
    clk,
    pc,
    data_addr,
    r_en,
    w_en,
    //pc_en,

    reset
);

input		clk;
input   [15:0]  pc;
//input		pc_en;
input   [15:0]  data_addr;
input           r_en;
input           w_en;
output          reset;

// MACROS ///////////////////////////////////////////
parameter SDATA_BASE = 16'hb00;
parameter SDATA_SIZE = 16'hC00;
//
parameter HMAC_BASE = 16'h1800;
parameter HMAC_SIZE = 16'h0020;
//
parameter SMEM_BASE = 16'hA100;
parameter LAST_SMEM_ADDR = 16'hBFFE;
parameter SMEM_SIZE = LAST_SMEM_ADDR - SMEM_BASE;
//
parameter KMEM_BASE = 16'h6A00;
parameter KMEM_SIZE = 16'h001F;

parameter INTR_BASE = 16'h0160; //16'h0130;
parameter INTR_SIZE = 16'h001F; //16'h00D0;

parameter CTR_BASE = 16'hFFC0;
parameter CTR_SIZE = 16'h001F;

parameter UART_BASE = 16'h0080;
parameter UART_SIZE = 16'h0005;

parameter LEDS = 16'h0019;
/////////////////////////////////////////////////////


parameter RESET_HANDLER = 16'hfffe;
parameter RUN  = 1'b0, KILL = 1'b1;
//-------------Internal Variables---------------------------
reg             state;
reg             key_res;
//

initial
    begin
        state = RUN;
        key_res = 1'b0;
    end

wire pc_not_in_srom = pc < SMEM_BASE || pc > LAST_SMEM_ADDR;
wire pc_in_srom = !pc_not_in_srom;

wire daddr_not_in_sdata = data_addr < SDATA_BASE || data_addr > SDATA_BASE + SDATA_SIZE;// -1;
wire daddr_in_sdata = !daddr_not_in_sdata;

wire daddr_not_in_krom = data_addr < KMEM_BASE || data_addr > KMEM_BASE + KMEM_SIZE;// -1;
wire daddr_in_krom = !daddr_not_in_krom;

wire daddr_not_in_HMAC = data_addr < HMAC_BASE || data_addr > HMAC_BASE + HMAC_SIZE;// -1;
wire daddr_in_HMAC = !daddr_not_in_HMAC;

wire daddr_not_in_ctr = data_addr < CTR_BASE || data_addr > CTR_BASE + CTR_SIZE;// -1;
wire daddr_in_ctr = !daddr_not_in_ctr;

// wire daddr_not_in_UART = data_addr < UART_BASE || data_addr > UART_BASE + UART_SIZE;
// wire daddr_not_in_LEDs = data_addr != LEDS;

wire violation1 = pc_not_in_srom && daddr_in_sdata && (r_en || w_en);
//wire violation2 = pc_in_srom && w_en && daddr_not_in_sdata && daddr_not_in_HMAC && daddr_not_in_ctr;// && daddr_not_in_UART && daddr_not_in_LEDs;
wire violation2 = 0;
wire violation3 = pc_not_in_srom && daddr_in_ctr && w_en;

// State transition logic//////
always @(posedge clk)
if(state == RUN && violation1)
    state <= KILL;
else if (state == RUN && violation2)
    state <= KILL;
else if (state == RUN && violation3)
    state <= KILL;
else if (state == KILL && (pc == RESET_HANDLER) && !violation1 && !violation2 && !violation3)
    state <= RUN;
else state <= state;
//////////////////////////////

// Output logic //////////////
always @(posedge clk)
if( 
    (state == RUN && violation1) ||
    (state == RUN && violation2) ||
    (state == RUN && violation3)
)
    key_res <= 1'b1;
else if (state == KILL && pc == RESET_HANDLER && !violation1 && !violation2 && !violation3)
    key_res <= 1'b0;
else if (state == KILL)
    key_res <= 1'b1;
else
    key_res <= 1'b0;

/////////////////////////////

assign reset = key_res;

endmodule