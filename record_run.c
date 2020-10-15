#include <stdint.h>
#include "pru_uart.h"
#include "pru_ecap.h" 


#define position_var ((struct other_pru_vars *)0x00002000)
#define sharedpru_vars ((struct shared_pru_vars *)0x00000000)

typedef uint8_t u8;


struct Timestamp {
			uint32_t s;
			uint32_t ns;
		};




struct other_pru_vars {
                        uint32_t position;
                };


struct shared_pru_vars {
			struct Timestamp time; 
			uint32_t position;
                        uint8_t force;
			uint8_t duty_cycle;
			uint8_t wave_form;
       			char response[8];
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
	
	for( i = 0; i < len; i++)
		sharedpru_vars->response[i] = msg[i];
   	return value;
}



struct Timestamp timestamp()
{
	static struct Timestamp now = {};
	uint32_t ns = CT_ECAP.TSCTR * 5;
	if( ns < now.ns )
		++now.s;
	now.ns = ns;
	return now;
}

void main()
{
        uint8_t force = 0; 
        
	CT_UART.THR = 'S';
        CT_UART.THR = 'N';
        CT_UART.THR = '\r';
        
        for(;;) {
                
        // parse and interpret message from load cell
		force = receive_measurement();
 	// get time measurement
	 	struct Timestamp ts = timestamp();
		
	// update sharedVars for GUI access
        	sharedpru_vars->position = position_var->position; 
        	sharedpru_vars->force = force;
		sharedpru_vars->time.ns = ts.ns;
		sharedpru_vars->time.s = ts.s;
		sharedpru_vars->duty_cycle = 0;
		sharedpru_vars->wave_form = 0;
        }
}
