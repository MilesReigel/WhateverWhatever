#include <iostream>

using namespace std;

// Take vector coefficient inputs 
void input();

// Arrange into an array
// Take determinant of array
// Create string output

int main()
{
    

    return 0;
}

void input()
{
    int coef[2][3];
    for (int i = 0; i < 6; i++)
    {
        cout << "Input coefficient " << i + 1 << ": " << endl;
        if (i < 3 )
        {
            cin >> coef[0][i];
        }
        else
        {
            cin >> coef[1][i-3];
        }
    } 
}