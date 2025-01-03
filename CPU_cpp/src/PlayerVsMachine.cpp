#include "Engine.h"
#include "GUI.h"
#include "UserInput.h"
#include <chrono>

void playGame(bool isPlayerWhite, float maxComputationTime, int maxCallDepth, BoardState state, History history) {
    state.isPlayerWhite = isPlayerWhite;
    history.saveState(state);
    int currentPieces = state.whitePieces.count() + state.blackPieces.count();
    int previousPieces = state.whitePieces.count() + state.blackPieces.count();
    int turnsWithoutCapture = -1;

    while (true) {
        // Check if game has ended
        int outcome = isTerminalNode(state);
        if (outcome == 1) {
            print("White has won!");
        } else if (outcome == -1) {
            print("Black has won!");
        } else if (currentPieces != previousPieces) {
            turnsWithoutCapture = 0;
        } else {
            turnsWithoutCapture++;
            if (state.isFlyingPhaseWhite & state.isFlyingPhaseBlack & turnsWithoutCapture > 10 || turnsWithoutCapture > 50) {
                print("The game is a draw!");
                break;
            }
        }

        //show_position(state);

        // Input moves from human and computer
        if (state.isPlayerWhite == state.isTurnWhite) {
            playerMove(state, history);
        } else {
            callCount = 0;
            leafCount = 0;
            auto start = std::chrono::high_resolution_clock::now();

            auto [eval, newState] = minimax(state, 5, -10000, 10000, !isPlayerWhite);

            auto end = std::chrono::high_resolution_clock::now();
            std::chrono::duration<double> duration = end - start;

            std::cout << "There were " << callCount << " minimax calls (" << leafCount << " leafs) taking " << duration.count() << " seconds \n";
            std::cout << "Average call length: " << 1e6 * duration.count() / callCount << " µs\n";
            std::cout << "The current evaluation is: " << eval << "\n\n";

            checkValidity(newState);
            state = newState;
            history.saveState(state);
        }
    }
}