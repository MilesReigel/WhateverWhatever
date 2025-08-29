#include <iostream>

using namespace std;

// Take determinant of array
// Create string output

// Take vector coefficient inputs,
// Arrange into an array
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
    int icoef = ((coef[0][1])*(coef[1][2])-(coef[0][2])*(coef[1][1]));
    int jcoef = ((coef[0][2])*(coef[1][0])-(coef[0][0])*(coef[1][2]));
    int kcoef = ((coef[0][0])*(coef[1][1])-(coef[0][1])*(coef[1][0]));
}

int main()
{
    input();

    return 0;
}