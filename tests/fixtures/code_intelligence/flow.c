extern void escape(int *value);

int branch_merge(int input)
{
    int value;
    if (input > 0)
        value = input + 1;
    else
        value = input - 1;
    return value;
}

int loop_switch(int n)
{
    int sum = 0;
    for (int i = 0; i < n; ++i) {
        if (i == 2) continue;
        if (i == 9) break;
        sum += i;
    }
    switch (sum) {
    case 0: return 10;
    case 1: return 20;
    default: return sum;
    }
}

int short_circuit(int a, int b)
{
    if (a && b) return a;
    return b;
}

int pointer_boundary(int input)
{
    int value = input;
    escape(&value);
    return value;
}

int select_value(int flag, int value)
{
    return flag ? value + 1 : value - 1;
}
