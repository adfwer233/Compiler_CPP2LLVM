#include <iostream>
#include <cstring>
using namespace std;

int main() {
	char stringc[50];
	cin >> stringc;
	int len = strlen(stringc);
	int IsPLD = 0;
	for (int i = 0; i + i < len && IsPLD != 1; i = i + 1) 
	{
		if (stringc[len - 1 - i] != stringc[i]) 
		{
			cout << "False";
			IsPLD = 1;
		}
	}
	if (!IsPLD) {
		cout << "True";
	}
	return 0;
}