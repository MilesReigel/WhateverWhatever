#include <iostream>

using namespace std;

void input2x2()
{
    int coef2x2[2][2];
    for (int i = 0; i < 4; i++)
    {
        cout << "Input coefficients one at a time, left to right and top to bottom: " << endl;
        if (i < 2)
        {
            cin >> coef2x2[0][i];
        }
        else
        {
            cin >> coef2x2[1][i];
        }
    }
    int output = ((coef2x2[0][0] * coef2x2[1][1]) - (coef2x2[0][1] * coef2x2[1][0]));
    cout << output;
}

void input3x3()
{
    int coef[3][3];
    for (int i = 0; i < 9; i++)
    {
        cout << "Input coefficients one at a time, left to right and top to bottom: " << endl;
        if (i < 3)
        {
            cin >> coef[0][i];
        }
        else if (3 < i && i < 7)
        {
            cin >> coef[1][i - 3];
        }
        else
        {
            cin >> coef[2][i-6];
        }
    }
    int x = (coef[0][0])*(((coef[1][1])*(coef[2][2])) - (coef[1][2])*(coef[2][1]));
    int y = (coef[0][1])*(((coef[1][2])*(coef[2][0])) - (coef[1][0])*(coef[2][2]));
    int z = (coef[0][2])*(((coef[1][0])*(coef[2][1])) - (coef[1][1])*(coef[2][0]));
    int output = x + y + z;
    cout << output;
}

void inputCross()
{
    int coef[2][3];
    for (int i = 0; i < 6; i++)
    {
        cout << "Input coefficients one at a time, left to right and top to bottom: " << endl;
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

    cout << "Your cross-product is: ";
    cout << icoef << "X + " << jcoef << "Y + " << kcoef << "Z." << endl;
}

int main()
{
    string choice;
    cout << "What kind of determinant would you like to take?" << endl; 
    cout << "The options are A)2x2, B)3x3, or C)Vector Cross Product" << endl;
    cin >> choice;

    if (choice == "a" || "A")
    {
        input2x2();
    } 
    else if (choice == "b" || "B")
    {
        input3x3();
    }
    else
    {
        inputCross();
    }

    return 0;
}