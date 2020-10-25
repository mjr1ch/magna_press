#include <stdint.h>
#include "pru_uart.h"
#include "pru_ecap.h" 

struct SharedVars {
    uint32_t position;
    int32_t force;
    uint8_t duty_cycle;
    uint8_t wave_form;
};

// encoder position in other PRU core's memory
#define position_var ((uint32_t const volatile *)0x00002000)

// strcuture holding PRU variables from the loop
far struct SharedVars volatile shared_pru1_vars __attribute__((location(0x10000)));

// receive byte from uart
static inline char uart_recv_byte()
{
    for(;;) {
        uint8_t lsr = CT_UART.LSR;
        if( lsr & 0x1e )
            __halt();  // receive-error occurred
        if( lsr & 0x01 )
            return (char) CT_UART.RBR;
    }
}


// receive CR-terminated line from uart
static inline uint8_t uart_recv_line( char volatile msg[], uint8_t maxlen )
{
    uint8_t len = 0;

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

// receive and parse measurement message from load cell
int32_t receive_measurement()
{
    // allocate buffer at fixed address for debugging convenience
    static char volatile msg[8] __attribute__((location(0x1f00)));

    // receive line from uart
    uint8_t len = uart_recv_line( msg, sizeof msg );

    // verify length and prefix
    if( len != 8 || msg[0] != 'N' || (msg[1] != '+' && msg[1] != '-'))
        __halt();

    // parse the remainder as integer
    int32_t value = 0;
    uint8_t i;
    for( i = 2; i < len; i++ ) {
        if( msg[i] < '0' || msg[i] > '9' )
            __halt();
        value = value * 10 + ( msg[i] - '0' );
    }
    if (msg[1] == '-')
            value *= -1;

    return value;
}



void main()
{
        uint32_t position =0;;
        int32_t force = 0; 
        
	CT_UART.THR = 'S'; 
        CT_UART.THR = 'N'; 
        CT_UART.THR = '\r';
        
        for(;;) {
		// parse and interpret message from load cell
                force = receive_measurement();
		
		// read position value from decoder 

 		position = *position_var;
        
		// update sharedVars for GUI access
                shared_pru1_vars.position = position;
                shared_pru1_vars.force = force;
	}
}

