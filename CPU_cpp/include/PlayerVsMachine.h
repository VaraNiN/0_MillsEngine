#ifndef PLAYERVSMACHINE_H
#define PLAYERVSMACHINE_H

#include "Engine.h"
#include "GUI.h"
#include "UserInput.h"

void playGame(bool isPlayerWhite, float maxComputationTime = 10., int maxCallDepth = 100, BoardState state = BoardState(), History history = History());

#endif // PLAYERVSMACHINE_H