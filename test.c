#include <stdio.h>
#include <stdint.h>
#include <string.h>

typedef uint8_t u8;

#define position_var *(uint32_t volatile *)0x208C

char* subString (const char* input, int offset, int len, char* dest)
{
  int input_len = strlen (input);

  if (offset + len > input_len)
  {
     return NULL;
  }

  strncpy (dest, input + offset, len);
  return dest;
}

 
void main()
{
	int c1 = 2;
        int c2 = 0;	
	static char msg[24] = "N+001.000";
	printf("Message value is: %s\n",msg);
	int length = *(&msg + 1) - msg;
	printf("The Size of the message is %i\n",length);
	char value[21];
	while (c1 < length) {
      		value[c2] = msg[c1];
      		c1++;
		c2++;
   	} 
	printf("Value is: %s\n",value);
}
