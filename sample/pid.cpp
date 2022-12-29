int printf(char* a, ...);
int scanf(char* a, ...);

int main() {

	int len = 0;
	scanf("%d", &len)

	char stringc[50];
	scanf("%s", stringc)
	
	int IsPLD = 0;
	int i = 0;
	for (i = 0; i + i < len && IsPLD != 1; i = i + 1) 
	{
		if (stringc[len - 1 - i] != stringc[i]) 
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