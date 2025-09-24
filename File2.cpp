#include <iostream>

using namespace std;

int headsize, midsize, lowsize;

int calculateTime(int target_size)
{
    int count = 0;
    for (int i = 0; i < target_size; i += i)
    {
        count += 1;
    }
    return(count);
}

void errorHandling(int &sizevar, string part)
{
    if (sizevar <= 0)
    {
        cout << "Please enter a positive integer for " << part << " size: ";
        cin >> sizevar;
        errorHandling(sizevar, part);
    }
    else
    {
        return;
    }
}

int main()
{
    cout << "Enter head size: " << endl;
    cin >> headsize;
    errorHandling(headsize, "Head");
    cout << calculateTime(headsize) << endl;
    
    cout << "Enter mid-body size: " << endl;
    cin >> midsize;
    errorHandling(midsize, "mid-body");
    cout << calculateTime(midsize) << endl; 
    
    cout << "Enter lower-body size: " << endl;
    cin >> lowsize;
    errorHandling(lowsize, "lower-body");
    cout << calculateTime(lowsize) << endl;
    
    return(0);
}
