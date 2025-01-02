#include "Engine.h"
#include "GUI.h"
#include "Utilities.h"

int main() {
    BoardState state;   //Current board position
    History history;    //History of all board positions
    history.saveState(state);

    int i = 1;
    while (true) {
        inputAdd(state, history);
        inputAdd(state, history);
        inputMove(state, history);
        inputMove(state, history);
    }

    return 0;
}