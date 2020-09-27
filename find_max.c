#include <stdint.h>
#include "pru_uart.h"
#include "pru_ecap.h" 


#define position_var ((struct other_pru_vars *)0x00002000)
#define findmax_vars ((struct shared_pru_vars *)0x00000000)

typedef uint8_t u8;

struct other_pru_vars {
                        uint32_t position;
                };


struct shared_pru_vars {
			uint64_t time; 
			uint32_t position;
                        uint8_t force;
                };

//far struct shared_pru_vars volatile *const findmax_vars __attribute__((location(0x10000)));
//far struct shared_pru_vars volatile findmax_vars __attribute__((location(0x10000)));


// receive byte from uart
static inline char uart_recv_byte()
{
    for(;;) {
        u8 lsr = CT_UART.LSR;
        if( lsr & 0x1e )
            __halt();  // receive-error occurred
        if( lsr & 0x01 )
            return (char) CT_UART.RBR;
    }
}

// receive CR-terminated line from uart
static inline unsigned uart_recv_line( char msg[], u8 maxlen )
{
    u8 len = 0;

    for(;;) {
        char c = uart_recv_byte();
        if( c == '\r' )
            break;  // found end of line
        if( len == maxlen )
            __halt();  // line does not fit in buffer
        msg[ len++ ] = c;
    }

    return len;
}

uint32_t receive_measurement()
{
    static char msg[8];
    u8 i;
    u8 len = uart_recv_line(msg, sizeof msg );
    if( len != 8 || msg[0] != 'N')
        __halt();
 
    uint32_t value = 0;
    for( i = 2; i < len; i++ ) {
        if( msg[i] < '0' || msg[i] > '9' )
            __halt();
        value = value * 10 + ( msg[i] - '0' );
    }
 
    return value;
}



uint64_t timestamp()
{
    	static uint64_t now = 0;
    	now += CT_ECAP.TSCTR - (uint32_t)now;
    	return now;
}


void main()
{
        uint32_t currentPosition;
        uint32_t maxForcePosition = 0;
        uint8_t force = 0; 
        uint8_t maxForce = 0;
        
	//CT_UART.THR = 'S';
        //CT_UART.THR = 'N';
        //CT_UART.THR = '\r';
	CT_ECAP.ECCTL1 = 1 << 15;  
	CT_ECAP.ECCTL2 = 1 << 4;
        
        for(;;) {
        	
		CT_UART.THR = 'G';
		CT_UART.THR = 'N';
		CT_UART.THR = '\r';
		force = receive_measurement();
                
        // parse and interpret message from load cell

        // read position value from decoder and run control loop
        	currentPosition = position_var->position;
        	if (force > maxForce){
                	maxForcePosition = currentPosition;
                	maxForce = force;
      	 	}
        // update sharedVars for GUI access
        	findmax_vars->position =  maxForcePosition;
        	findmax_vars->force = maxForce;
		findmax_vars->time = timestamp();
        }
}
