// Entry point: dispatch draft and gameplay; a failed turn is logged and still yields.
#include <cambc.h>

#include <iostream>

#include "bot.h"
#include "draft.h"

int main() {
    Bot bot;
    while (true) {
        try {
            if (cambc::is_draft())
                play_draft();
            else {
                const auto started = cambc::round_number();
                bot.play_turn();
                // Out of fuel means the engine paused us mid-turn and resumed a later round.
                if (cambc::round_number() != started)
                    std::cout << "goldrush warning: turn ran out of fuel (round " << started << ")" << std::endl;
            }
        } catch (const std::exception& error) {  // never let one bad turn crash the bot
            std::cout << "goldrush error: " << error.what() << std::endl;
        } catch (...) {
            std::cout << "goldrush error: unknown exception" << std::endl;
        }
        cambc::end_turn();
    }
}
