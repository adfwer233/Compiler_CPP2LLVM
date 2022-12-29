#include <iostream>
#include <cstring>
using namespace std;

int arr[50];
int maxlen;

void QuickSort(int low, int high)
{
    if (low < high)
    {
        int i = low;
        int j = high;
        int k = arr[low];
        while (i < j)
        {
            while (i < j && arr[j] >= k)
            {
                j--;
            }

            if (i < j)
            {
                arr[i++] = arr[j];
            }

            while (i < j && arr[i] < k)
            {
                i++;
            }

            if (i < j)
            {
                arr[j--] = arr[i];
            }
        }

        arr[i] = k;
        QuickSort(low, i - 1);
        QuickSort(i + 1, high);
    }
}

int main()
{
    cin >> maxlen;
    int i = 0, j = 0, t = 0;
    for (i = 0; i < maxlen; i = i + 1)
    {
        cin >> arr[i];
    }

    QuickSort(0, maxlen - 1);

    for (i = 0; i < maxlen; i++)
    {
        cout << arr[i] << " ";
    }

    return 0;
}
