#include <iostream>
#include <stdlib.h>
#include <string.h>

int main() {
	char string[1002];
	scanf("%s", string);
	int len = strlen(string);
	int IsPLD = 0;
	for (int i = 0; i + i < len && IsPLD != 1; i = i + 1) 
	{
		if (string[len - 1 - i] != string[i]) 
		{
			printf("False");
			IsPLD = 1;
		}
	}
	if (!IsPLD) {
		printf("True");
	}
	return 0;
}