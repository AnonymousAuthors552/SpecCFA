
module  acfa_memory (

// OUTPUTs
    per_dout,                       // Peripheral data output
    ER_min,                          // VAPE ER_min
    ER_max,                          // VAPE ER_max

// INPUTs
    mclk,                           // Main system clock
    per_addr,                       // Peripheral address
    per_din,                        // Peripheral data input
    per_en,                         // Peripheral enable (high active)
    per_we,                         // Peripheral write enable (high active)
  
    cflow_logs_ptr_din,             // Control Flow: pointer to logs being modified
    puc_rst                         // Main system reset
);

// OUTPUTs
//=========
output      [15:0] per_dout;        // Peripheral data output
output      [15:0] ER_min;                          // VAPE ER_min
output      [15:0] ER_max;                          // VAPE ER_max

// INPUTs
//=========

input              mclk;            // Main system clock
input       [13:0] per_addr;        // Peripheral address
input       [15:0] per_din;         // Peripheral data input
input              per_en;          // Peripheral enable (high active)
input        [1:0] per_we;          // Peripheral write enable (high active)
input              puc_rst;         // Main system reset
input       [15:0] cflow_logs_ptr_din;  // Control Flow: pointer to logs being modified


//=============================================================================
// 1)  PARAMETER DECLARATION
//=============================================================================

// ACFA metadta consists of
//  - 32*8 = 16*16 = 256 bits of challenge
//  - 16 bits of AER_min
//  - 16 bits of AER_max
//  - 16 bits of current log pointer  
 
parameter       [14:0] METADATA_BASE_ADDR = CHAL_BASE_ADDR+CHAL_SIZE;    // 0x1a0  
parameter       [13:0] METADATA_PER_ADDR = METADATA_BASE_ADDR[14:1];                 
parameter              METADATA_SIZE = 6; 
                                                            
// Decoder bit width (defines how many bits are considered)
parameter              DEC_WD      =  3;                 // sizeof(METADATA))-1 
                                                          
// Register addresses offset                             
parameter [DEC_WD-1:0] ERMIN      =  'h0,             //0x1a0
                       ERMAX      =  'h1,             //0x1a2
                       CLOGP      =  'h2;             //0x1a4         

// Register one-hot decoder utilities                    
parameter              DEC_SZ      =  (1 << DEC_WD);        
parameter [DEC_SZ-1:0] BASE_REG   =  {{DEC_SZ-1{1'b0}}, 1'b1};
                                                         
// Register one-hot decoder                              
parameter [DEC_SZ-1:0] ERMIN_D  = (BASE_REG << ERMIN),  
                       ERMAX_D  = (BASE_REG << ERMAX),
                       CLOGP_D  = (BASE_REG << CLOGP);
                       
//============================================================================
// 2)  REGISTER DECODER
//============================================================================

// Local register selection
wire              reg_sel      =  per_en & (per_addr[13:DEC_WD-1]==METADATA_BASE_ADDR[14:DEC_WD]);

// Register local address
wire [DEC_WD-1:0] reg_addr     =  {1'b0, per_addr[DEC_WD-2:0]};

// Register address decode
wire [DEC_SZ-1:0] reg_dec      = (ERMIN_D  &  {DEC_SZ{(reg_addr==ERMIN)}}) |
                                 (ERMAX_D  &  {DEC_SZ{(reg_addr==ERMAX)}}) |
                                 (CLOGP_D  &  {DEC_SZ{(reg_addr==CLOGP)}});
//                                  |
//                                 (EXECFLAG_D  &  {DEC_SZ{(reg_addr==EXECFLAG)}}) | 
//                                 (LOGSIZE_D  &  {DEC_SZ{(reg_addr==LOGSIZE)}});
                                 
// Read/Write probes
wire              reg_write =  |per_we & reg_sel;
wire              reg_read  = ~|per_we & reg_sel;

// Read/Write vectors
wire [DEC_SZ-1:0] reg_wr    = reg_dec & {512{reg_write}};
wire [DEC_SZ-1:0] reg_rd    = reg_dec & {512{reg_read}};


//============================================================================
// 3) REGISTERS
//============================================================================ 

// ER_min Register 
//-----------------
reg  [15:0] ermin;

wire        ermin_wr  = reg_wr[ERMIN];
wire [15:0] ermin_nxt = per_din;
 
always @ (posedge mclk or posedge puc_rst)
  if (puc_rst)        ermin <=  16'h0;
  else if (ermin_wr)  ermin <=  ermin_nxt; 
  
// ER_max Register
//-----------------
reg  [15:0] ermax;

wire       ermax_wr  = reg_wr[ERMAX];
wire [15:0] ermax_nxt = per_din;

always @ (posedge mclk or posedge puc_rst)
if (puc_rst)        ermax <=  16'h0;
else if (ermax_wr) ermax <=  ermax_nxt;

// Cflow_logs_pointer Register
//----------------------------
reg   [15:0] cflow_logs_ptr; 

always @ (posedge mclk or posedge puc_rst)
if (puc_rst)        cflow_logs_ptr <=  16'h0;
else                cflow_logs_ptr <=  cflow_logs_ptr_din;
  
// Challenge Register
//----------------- 
// Register base address (must be aligned to decoder bit width)
parameter       [14:0] BASE_ADDR   = 15'h0180; 
 
parameter              CHAL_SIZE  =  32;            // 32 bytes              
parameter              CHAL_ADDR_MSB   = 3;         // Address stored in 16-bit registers, address 32*8 bits using 16-bit registers, need 4 bits -> 3 MSB (start from 0)    
 
parameter       [14:0] CHAL_BASE_ADDR = BASE_ADDR;              // 0x180 
   
parameter       [13:0] CHAL_PER_ADDR  = CHAL_BASE_ADDR[14:1];   

wire   [CHAL_ADDR_MSB:0] chal_addr_reg = per_addr-CHAL_PER_ADDR; 
wire                     chal_cen      = per_en & per_addr >= CHAL_PER_ADDR & per_addr < CHAL_PER_ADDR+(CHAL_SIZE*8/16);
wire    [15:0]           chal_dout;
wire    [1:0]            chal_wen      = per_we & {2{per_en}};

chalmem #(CHAL_ADDR_MSB, CHAL_SIZE)
challenges (  

    // OUTPUTs
    .ram_dout    (chal_dout),           // Program Memory data output
    // INPUTs
    .ram_addr    (chal_addr_reg),       // Program Memory address
    .ram_cen     (~chal_cen),           // Program Memory chip enable (low active)
    .ram_clk     (mclk),                // Program Memory clock
    .ram_din     (per_din),             // Program Memory data input
    .ram_wen     (~chal_wen)            // Program Memory write enable (low active)
);
wire [15:0]           chal_rd = chal_dout & {16{chal_cen & ~|per_we}};

initial begin
    ermin <= 16'haa11; 
    ermax <= 16'habcd;
    cflow_logs_ptr <= 16'h0000;
end

//============================================================================
// 4) DATA OUTPUT GENERATION
//============================================================================

// Data output mux
wire [15:0] ermin_rd     = ermin             & {16{reg_rd[ERMIN]}};
wire [15:0] ermax_rd     = ermax             & {16{reg_rd[ERMAX]}};
wire [15:0] cflow_logs_ptr_rd     = cflow_logs_ptr & {16{reg_rd[CLOGP]}};

wire [15:0] per_dout  =  ermin_rd  |
                         ermax_rd  |
                         cflow_logs_ptr_rd |
                         chal_rd;
                         
wire [15:0] ER_min = ermin;
wire [15:0] ER_max = ermax;
 
endmodule 