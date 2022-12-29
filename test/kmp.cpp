#include <iostream>
#include <cstring>
using namespace std;

int main() {
	char S_string[50];
	char T_string[50];
	int next[50];
	next[0] = -1;
	int lenS_string, lenT_string;
	cout << "Source string" << endl;
	cin >> S_string;
	cout << "Pattern string: " << endl;
	cin >> T_string;
    lenS_string = strlen(S_string);
	lenT_string = strlen(T_string);

	int i, j;
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
            cout << res << endl;
			j = next[j];
		}
	}
	if (flag == 0){
		cout << "False" << endl;
    }
	return 0;
}