module tb;

    reg[7:0] a;
    wire[2:0] b;
    wire v;

    priorityEncoder8 bigp (a, b, v);

    initial begin
        #1
        if (v == 1) $display("Big uh oh for a = 0");
        
        for (a = 0; a < 7; a = a + 1) begin
            

        end

    end

endmodule

// This is a buggy 8-input priority encoder
module priorityEncoder8(input [7:0]in, output [2:0] out, output valid);
    assign out = 
    in[7] ? 3'b111 : 
    in[6] ? 3'b110 : 
    in[5] ? 3'b110 : 
    in[4] ? 3'b100 : 
    in[3] ? 3'b011 : 
    in[2] ? 3'b011 : 
    in[1] ? 3'b001 : 
    in[0] ? 3'b000 : 3'b000;
assign valid = |in;
endmodule
