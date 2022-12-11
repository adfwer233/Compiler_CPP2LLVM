#include <iostream>
#include <stdio.h>
#include <stdlib.h>

int arr[1001];
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
    scanf("%d", &maxlen);
    int i, j, t;
    for (i = 0; i < maxlen; i = i + 1)
    {
        scanf("%d", &arr[i]);
    }

    QuickSort(0, maxlen - 1);

    for (i = 0; i < maxlen; i++)
    {
        printf("%d ", arr[i]);
    }

    return 0;
}