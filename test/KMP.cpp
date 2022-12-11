#include <iostream>
#include <stdlib.h>
#include <string.h>

int main() {
	char S_string[500];
	char T_string[500];
	int next[500];
	next[0] = -1;
	int lenS_string, lenT_string;
	printf("Source string: ");
	scanf("%s", S_string);
	printf("Pattern string: ");
	scanf("%s", T_string);
    lenS_string = strlen(S_string);
	lenT_string = strlen(T_string);
	
	for (int i = 1, j = -1; i < lenT_string;  i = i + 1) 
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
	for (int i = 0, j = -1; i < lenS_string; i = i + 1) 
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
			printf("%d\n", i - j);
			j = next[j];
		}
	}
	if (flag == 0){
		printf("False\n");
    }
	return 0;
}