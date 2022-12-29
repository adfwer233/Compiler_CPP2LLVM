int printf(char* a, ...);
int scanf(char* a, ...);

//#include "stdio.h"

int arr[50];
int maxlen = 0;

void QuickSort(int low, int high)
{
    printf("%d %d\n", low, high);
    if (low < high)
    {
        int i = low;
        int j = high;
        int k = arr[low];
        while (i < j)
        {
            while (i < j && arr[j] >= k)
            {
                j = j - 1;
            }

            if (i < j)
            {
                arr[i] = arr[j];
                i = i + 1;
            }

            while (i < j && arr[i] < k)
            {
                i = i + 1;
            }

            if (i < j)
            {
                arr[j] = arr[i];
                j = j - 1;
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
    int i = 0;
    int j = 0;
    int t = 0;
    for (i = 0; i < maxlen; i = i + 1)
    {
        scanf("%d", &arr[i]);
    }
    for (i = 0; i < maxlen; i=i+1)
    {
        printf("%d ", arr[i]);
    }
    printf("\n")
    QuickSort(0, maxlen - 1);

    for (i = 0; i < maxlen; i=i+1)
    {
        printf("%d ", arr[i]);
    }

    return 0;
}
