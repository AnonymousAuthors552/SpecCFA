//----------------------------------------------------------------------------
// Copyright (C) 2001 Authors
//
// This source file may be used and distributed without restriction provided
// that this copyright statement is not removed from the file and that any
// derivative work contains the original copyright notice and the associated
// disclaimer.
//
// This source file is free software; you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published
// by the Free Software Foundation; either version 2.1 of the License, or
// (at your option) any later version.
//
// This source is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
// FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
// License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with this source; if not, write to the Free Software Foundation,
// Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
//
//----------------------------------------------------------------------------
// 
// *File Name: ram.v
// 
// *Module Description:
//                      Scalable RAM model
//
// *Author(s):
//              - Olivier Girard,    olgirard@gmail.com
//
//----------------------------------------------------------------------------
// $Rev$
// $LastChangedBy$
// $LastChangedDate$
//----------------------------------------------------------------------------

module blockmem (

// OUTPUTs
    ram_dout,                      // RAM data output
    block_entry_src,
    block_entry_dest,
    block_len,
    block_id,

// INPUTs
    block_ptr,
    block_base,
    ram_addr,                      // RAM address
    ram_cen,                       // RAM chip enable (low active)
    ram_clk,                       // RAM clock
    ram_din,                       // RAM data input
    ram_wen                        // RAM write enable (low active)
);

// PARAMETERs
//============
parameter ADDR_MSB   =  6;         // MSB of the address bus
parameter MEM_SIZE   =  256;       // Memory size in bytes


// OUTPUTs
//============
output      [15:0] ram_dout;       // RAM data output
output [15:0] block_entry_src;
output [15:0] block_entry_dest;
output [7:0] block_len;
output [7:0] block_id;

//============
input         [15:0] block_ptr;
input         [15:0] block_base;
input [ADDR_MSB:0] ram_addr;       // RAM address
input              ram_cen;        // RAM chip enable (low active)
input              ram_clk;        // RAM clock
input       [15:0] ram_din;        // RAM data input
input        [1:0] ram_wen;        // RAM write enable (low active)
//


// RAM
//============
(* ram_style = "block" *) reg         [15:0] blockmem [0:(MEM_SIZE/2)-1];
reg         [ADDR_MSB:0] ram_addr_reg;
wire        [15:0] mem_val = blockmem[ram_addr];

//for debug
wire         [ADDR_MSB:0] block_src_addr = block_base+block_ptr+1;
wire         [ADDR_MSB:0] block_dest_addr = block_base+block_ptr+2;

assign block_id = blockmem[block_base][15:8];
assign block_len = blockmem[block_base][7:0];
assign block_entry_src = blockmem[block_src_addr];
assign block_entry_dest = blockmem[block_dest_addr];

integer i;
initial 
begin
    for(i=0; i<MEM_SIZE; i=i+1) begin
        blockmem[i] <= 0;
    end
    ram_addr_reg <= 0;
end
  
always @(posedge ram_clk)
begin
    ram_addr_reg <= ram_addr;
    if (~ram_cen & ram_addr<(MEM_SIZE/2))
    begin
        if      (ram_wen==2'b00) blockmem[ram_addr]        <= ram_din;
        else if (ram_wen==2'b01) blockmem[ram_addr][15:8]  <= ram_din[15:8]; //  <= {ram_din[15:8], mem_val[7:0]};
        else if (ram_wen==2'b10) blockmem[ram_addr][7:0]   <= ram_din[7:0]; // <= {mem_val[15:8], ram_din[7:0]};
    end
end

assign ram_dout = blockmem[ram_addr_reg];

endmodule // blockmem
