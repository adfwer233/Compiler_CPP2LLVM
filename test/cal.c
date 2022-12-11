#include <stdlib.h>
#include <string.h>

int main() {
	char StringGet[1002];
	gets(StringGet);
	int len = strlen(StringGet);
	int IsPLD = 0;
	for (int i = 0; i + i < len && IsPLD != 1; i = i + 1) 
	{
		if (StringGet[len - 1 - i] != StringGet[i]) 
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