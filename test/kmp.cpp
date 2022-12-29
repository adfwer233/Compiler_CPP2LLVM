int printf(char* a, ...);
int scanf(char* a, ...);

int main() {
	int lenS_string = 0; 
	int lenT_string = 0;

	scanf("%d %d", &lenS_string, &lenT_string);

	char S_string[50];
	char T_string[50];
	int next[50];
	next[0] = -1;
	printf("Source string:\n");
	scanf("%s", S_string);
	printf("Pattern string:\n");
	scanf("%s", T_string);

	int i = 0
	int j = 0;
	for (i = 1, j = -1; i < lenT_string;  i = i + 1) 
	{
        while(j >= 0 && T_string[i] != T_string[j+1])
        {
            j = next[j];
        }
		if (T_string[i] == T_string[j+1]) 
		{
            j = j + 1;
        }
		next[i] = j;
	}
	int flag = 0;

	for (i = 0, j = -1; i < lenS_string; i = i + 1) 
	{
        while(j >= 0 && S_string[i] != T_string[j+1])
        {
            j = next[j];
        }
		if (S_string[i] == T_string[j+1]) 
		{
            j = j + 1;
        }
		if (j + 1 == lenT_string) 
		{
			flag = 1;
            int res = i - j;
            printf("%d ", res);
			j = next[j];
		}
	}
	if (flag == 0){
		printf("False");
    }
	return 0;
}