#include "Engine.h"
#include "GUI.h"
#include "Utilities.h"
#include "UserInput.h"
#include <iostream>
#include <bitset>

int main() {
    BoardState state;   //Current board position
    History history;    //History of all board positions
    history.saveState(state);

    float eval = evaluate(state);

    while (true) {
        eval = evaluate(state);
        print(eval);
        inputAdd(state, history);
    }


    //state.whitePieces = generateRandomBitset();
    //state.blackPieces = generateRandomBitset();
    //timeStuff(state);

    return 0;
}