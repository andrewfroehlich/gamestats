"""
Craps Game Simulator

Simulates various betting strategies in Craps to analyze expected outcomes over many rounds.
Supports multiple bet types:
- Pass Line / Don't Pass with odds
- Multi-roll side bets (low numbers, high numbers, all numbers)
- Single-roll bets (field, twelve)

Runs multiple simulations and provides statistical analysis of results.
"""

import random

### CONFIGURATION SECTION ###

# Simulation mode: 'fixed_rounds' or 'threshold'
simulation_mode = 'threshold'  # 'fixed_rounds' runs a set number of rounds, 'threshold' runs until win/loss threshold

# Fixed rounds mode settings
total_rounds = 5000  # number of rounds per simulation (only used in 'fixed_rounds' mode)
                     # A round is until: comeout win/loss, point made, or seven out

# Threshold mode settings
win_threshold = 100  # Stop simulation when bankroll reaches this amount (only used in 'threshold' mode)
loss_threshold = -100  # Stop simulation when bankroll reaches this amount (only used in 'threshold' mode)
max_rounds = 100000  # Safety limit to prevent infinite loops in threshold mode

num_simulations = 10000  # number of times to run the full simulation
seed = None  # set to an integer for repeatable results, None for random
debug = False  # Enable detailed logging of each roll

strategy = 'dont_pass' # Choose betting strategy: 'pass_line' or 'dont_pass'

# Bet amounts (in dollars)
bet_pass_line = 3  # Main pass line bet
bet_odds = 3  # Odds bet (placed after point is established)
bet_low_numbers = 1  # Side bet: all low numbers (2-6) before 7
bet_high_numbers = 1  # Side bet: all high numbers (8-12) before 7
bet_all_numbers = 0  # Side bet: all numbers (2-6, 8-12) before 7
bet_field = 0  # Field bet (placed on every single dice roll)
bet_twelve = 0  # Single roll bet on 12 (pays 31:1)
### END CONFIGURATIONS SECTION ###

### INITIALIZATION ###

# Set seed for repeatability if specified
if seed is not None:
    random.seed(seed)

### GAME MECHANICS FUNCTIONS ###

def roll_dice():
    """Roll two dice and return the sum"""
    die1 = random.randint(1, 6)
    die2 = random.randint(1, 6)
    return die1 + die2

### PAYOUT CALCULATION FUNCTIONS ###

def calculate_field_payout(roll, field_bet):
    """Calculate payout for field bet using lookup table"""
    FIELD_PAYOUT = [0, 0, 2, 1, 1, -1, -1, -1, -1, 1, 1, 1, 2] # double on 2,12; single on 3,4,9,10,11
    return field_bet * FIELD_PAYOUT[roll]

def calculate_twelve_payout(roll, twelve_bet):
    """Calculate payout for twelve bet using lookup table"""
    TWELVE_PAYOUT = [0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 31]  # only pays on 12 (31:1)
    return twelve_bet * TWELVE_PAYOUT[roll]

def calculate_odds_payout(point, odds_bet, is_pass_line, won):
    """Calculate payout for odds bet using lookup tables"""
    if not won:
        return -odds_bet

    # Odds bet payout multipliers by point: [0,1,2,3, 4,   5,   6,  7, 8,   9,  10]
    PASS_ODDS_MULTIPLIER =      [0, 0, 0, 0, 2.0, 1.5, 1.2, 0, 1.2, 1.5, 2.0, 0, 0]  # 2:1, 3:2, 6:5
    DONT_PASS_ODDS_MULTIPLIER = [0, 0, 0, 0, 0.5, 2/3, 5/6, 0, 5/6, 2/3, 0.5, 0, 0]  # 1:2, 2:3, 5:6

    multiplier = PASS_ODDS_MULTIPLIER[point] if is_pass_line else DONT_PASS_ODDS_MULTIPLIER[point]
    return odds_bet * multiplier

### SIMULATION FUNCTIONS ###

def process_single_roll_bets(roll, roll_details):
    """Process field and twelve bets for a single roll, return total payout"""
    total_payout = 0

    # Field bet
    if bet_field > 0:
        field_payout = calculate_field_payout(roll, bet_field)
        total_payout += field_payout
        if debug and field_payout != 0:
            status = "WINS" if field_payout > 0 else "LOSES"
            roll_details.append(f"  Field bet {status} ${abs(field_payout)}")

    # Twelve bet
    if bet_twelve > 0:
        twelve_payout = calculate_twelve_payout(roll, bet_twelve)
        total_payout += twelve_payout
        if debug and twelve_payout != 0:
            status = "WINS" if twelve_payout > 0 else "loses"
            roll_details.append(f"  Twelve bet {status} ${abs(twelve_payout)}{'!' if twelve_payout > 0 else ''}")

    return total_payout

def create_result(total_payout, main_result, point, all_rolls, seven_rolled, roll_details):
    """Create a standardized result dictionary"""
    return {
        'total': total_payout,
        'main_result': main_result,
        'point': point,
        'all_rolls': all_rolls,
        'seven_rolled': seven_rolled,
        'roll_details': roll_details
    }

def simulate_round(use_pass_line=True, numbers_rolled_so_far=None, round_num=0):
    """
    Simulate a single pass/don't pass round
    Returns: dict with payout, numbers rolled, and whether a 7 was rolled
    """
    if numbers_rolled_so_far is None:
        numbers_rolled_so_far = set()

    total_payout = 0
    all_rolls = []  # Track every roll in this round
    roll_details = []  # Detailed info for each roll for debug

    # Place main bet
    main_bet = bet_pass_line
    total_payout -= main_bet  # Pay the bet

    if debug:
        bet_type = 'Pass Line' if use_pass_line else "Don't Pass"
        roll_details.append(f"Round {round_num}: Placed ${main_bet} on {bet_type}")

    come_out_roll = roll_dice()
    all_rolls.append(come_out_roll)

    # Process single-roll bets on come out roll
    total_payout += process_single_roll_bets(come_out_roll, roll_details)

    if debug:
        roll_details.append(f"  Come out roll: {come_out_roll}")

    if use_pass_line:
        # Pass line logic
        if come_out_roll in [7, 11]:
            # Natural win
            total_payout += main_bet * 2  # Return bet + winnings
            if debug:
                roll_details.append(f"  Natural {come_out_roll}! Pass Line WINS ${main_bet}")
            return create_result(total_payout, 'win', None, all_rolls, come_out_roll == 7, roll_details)
        elif come_out_roll in [2, 3, 12]:
            # Craps - lose
            if debug:
                roll_details.append(f"  Craps {come_out_roll}! Pass Line LOSES ${main_bet}")
            return create_result(total_payout, 'lose', None, all_rolls, False, roll_details)
    else:
        # Don't pass logic
        if come_out_roll in [2, 3]:
            # Win
            total_payout += main_bet * 2
            if debug:
                roll_details.append(f"  Craps {come_out_roll}! Don't Pass WINS ${main_bet}")
            return create_result(total_payout, 'win', None, all_rolls, False, roll_details)
        elif come_out_roll in [7, 11]:
            # Lose
            if debug:
                roll_details.append(f"  Natural {come_out_roll}! Don't Pass LOSES ${main_bet}")
            return create_result(total_payout, 'lose', None, all_rolls, come_out_roll == 7, roll_details)
        elif come_out_roll == 12:
            # Push - return bet
            total_payout += main_bet
            if debug:
                roll_details.append(f"  12! Don't Pass PUSH (no win/loss)")
            return create_result(total_payout, 'push', None, all_rolls, False, roll_details)

    # Point is established
    point = come_out_roll

    # Place odds bet
    total_payout -= bet_odds

    if debug:
        roll_details.append(f"  Point is {point}. Placed ${bet_odds} odds bet")

    # Roll until point or 7
    while True:
        roll = roll_dice()
        all_rolls.append(roll)

        # Process single-roll bets
        total_payout += process_single_roll_bets(roll, roll_details)

        if debug:
            roll_details.append(f"  Roll: {roll}")

        if use_pass_line:
            if roll == point:
                # Win - return main bet + winnings
                main_win = main_bet
                odds_win = calculate_odds_payout(point, bet_odds, True, True)
                total_payout += main_bet * 2
                total_payout += bet_odds + odds_win
                if debug:
                    roll_details.append(f"  Point {point} made! Pass Line WINS ${main_win}, Odds WINS ${odds_win}")
                return create_result(total_payout, 'win', point, all_rolls, False, roll_details)
            elif roll == 7:
                # Lose both bets (already subtracted)
                if debug:
                    roll_details.append(f"  Seven out! Pass Line LOSES ${main_bet}, Odds LOSES ${bet_odds}")
                return create_result(total_payout, 'lose', point, all_rolls, True, roll_details)
        else:
            if roll == 7:
                # Win for don't pass
                main_win = main_bet
                odds_win = calculate_odds_payout(point, bet_odds, False, True)
                total_payout += main_bet * 2
                total_payout += bet_odds + odds_win
                if debug:
                    roll_details.append(f"  Seven out! Don't Pass WINS ${main_win}, Odds WINS ${odds_win}")
                return create_result(total_payout, 'win', point, all_rolls, True, roll_details)
            elif roll == point:
                # Lose both bets (already subtracted)
                if debug:
                    roll_details.append(f"  Point {point} made! Don't Pass LOSES ${main_bet}, Odds LOSES ${bet_odds}")
                return create_result(total_payout, 'lose', point, all_rolls, False, roll_details)

def run_single_simulation(sim_num):
    """Run a single simulation until completion based on simulation_mode"""
    total_bankroll = 0
    low_hits = 0
    high_hits = 0
    all_hits = 0

    # Track single-roll bet statistics
    total_dice_rolls = 0
    twelve_hits = 0
    field_wins = 0

    # Track numbers for side bets (persist until 7 is rolled)
    numbers_rolled = set()
    low_numbers = {2, 3, 4, 5, 6}
    high_numbers = {8, 9, 10, 11, 12}
    all_numbers = low_numbers | high_numbers

    # Place initial side bets
    total_bankroll -= (bet_low_numbers + bet_high_numbers + bet_all_numbers)

    if debug:
        print(f"=== Starting Simulation {sim_num} ===")
        print(f"Initial side bets placed: Low=${bet_low_numbers}, High=${bet_high_numbers}, All=${bet_all_numbers}")
        print(f"Starting bankroll: ${total_bankroll:.2f}")
        print()

    run = 0
    while True:
        # Check termination conditions based on mode
        if simulation_mode == 'fixed_rounds':
            if run >= total_rounds:
                break
        elif simulation_mode == 'threshold':
            if total_bankroll >= win_threshold:
                break  # Hit win threshold
            if total_bankroll <= loss_threshold:
                break  # Hit loss threshold
            if run >= max_rounds:
                break  # Safety limit

        run += 1
        bankroll_before = total_bankroll

        result = simulate_round(use_pass_line=(strategy == 'pass_line'), round_num=run+1)
        total_bankroll += result['total']

        # Print roll details
        if debug:
            for detail in result.get('roll_details', []):
                print(detail)

        # Track single-roll bet statistics
        for roll in result['all_rolls']:
            total_dice_rolls += 1
            if roll == 12:
                twelve_hits += 1
            if roll in [2, 3, 4, 9, 10, 11, 12]:  # Field wins (including 2 and 12)
                field_wins += 1

        # Add all rolls to the numbers tracking (except 7s)
        new_numbers = []
        for roll in result['all_rolls']:
            if roll != 7:
                if roll not in numbers_rolled:
                    new_numbers.append(roll)
                numbers_rolled.add(roll)

        if debug and new_numbers:
            print(f"  New numbers for side bets: {new_numbers}")
            print(f"  Side bet tracker now has: {sorted(numbers_rolled)}")

        # If a 7 was rolled, check side bets and reset
        if result['seven_rolled']:
            side_bet_details = []

            # Check side bet wins
            if low_numbers.issubset(numbers_rolled):
                payout = bet_low_numbers * 31
                total_bankroll += bet_low_numbers * 32
                low_hits += 1
                side_bet_details.append(f"LOW NUMBERS HIT! Won ${payout}")

            if high_numbers.issubset(numbers_rolled):
                payout = bet_high_numbers * 31
                total_bankroll += bet_high_numbers * 32
                high_hits += 1
                side_bet_details.append(f"HIGH NUMBERS HIT! Won ${payout}")

            if all_numbers.issubset(numbers_rolled):
                payout = bet_all_numbers * 156
                total_bankroll += bet_all_numbers * 157
                all_hits += 1
                side_bet_details.append(f"ALL NUMBERS HIT! Won ${payout}")

            if debug:
                print(f"  SEVEN OUT - Side bets resolved:")
                if side_bet_details:
                    for detail in side_bet_details:
                        print(f"    {detail}")
                else:
                    print(f"    No side bet wins (had numbers: {sorted(numbers_rolled)})")

            # Reset for next side bet cycle
            numbers_rolled = set()

            # Place new side bets
            total_bankroll -= (bet_low_numbers + bet_high_numbers + bet_all_numbers)

            if debug:
                print(f"  New side bets placed: ${bet_low_numbers + bet_high_numbers + bet_all_numbers}")

        if debug:
            bankroll_change = total_bankroll - bankroll_before
            print(f"  Round result: {'+' if bankroll_change >= 0 else ''}${bankroll_change:.2f}")
            print(f"  Running bankroll: ${total_bankroll:.2f}")
            print()

    return {
        'final_bankroll': total_bankroll,
        'rounds_played': run,
        'low_hits': low_hits,
        'high_hits': high_hits,
        'all_hits': all_hits,
        'total_dice_rolls': total_dice_rolls,
        'twelve_hits': twelve_hits,
        'field_wins': field_wins
    }

def print_bet_statistics(avg_dice_rolls, avg_rounds, avg_low_hits, avg_high_hits, avg_all_hits,
                        avg_twelve_hits, avg_field_wins):
    """Print statistics for active bets only"""

    # Multi-roll side bets
    if bet_low_numbers > 0 or bet_high_numbers > 0 or bet_all_numbers > 0:
        print(f"\n=== Side Bet Statistics (multi-roll) ===")

        if bet_low_numbers > 0:
            print(f"Low numbers (2-6):")
            print(f"  Average hits per simulation: {avg_low_hits:.1f}")
            if avg_low_hits > 0:
                print(f"  Hit frequency: 1 in every {avg_rounds/avg_low_hits:.1f} rounds")

        if bet_high_numbers > 0:
            print(f"High numbers (8-12):")
            print(f"  Average hits per simulation: {avg_high_hits:.1f}")
            if avg_high_hits > 0:
                print(f"  Hit frequency: 1 in every {avg_rounds/avg_high_hits:.1f} rounds")

        if bet_all_numbers > 0:
            print(f"All numbers (2-6, 8-12):")
            print(f"  Average hits per simulation: {avg_all_hits:.1f}")
            if avg_all_hits > 0:
                print(f"  Hit frequency: 1 in every {avg_rounds/avg_all_hits:.1f} rounds")

    # Single-roll bets
    if bet_twelve > 0 or bet_field > 0:
        print(f"\n=== Single Roll Bet Statistics ===")
        print(f"Average dice rolls per simulation: {avg_dice_rolls:.0f}")

        if bet_twelve > 0:
            print(f"\nTwelve bet:")
            print(f"  Average hits per simulation: {avg_twelve_hits:.1f}")
            if avg_twelve_hits > 0:
                print(f"  Hit frequency: 1 in every {avg_dice_rolls/avg_twelve_hits:.1f} rolls")
                print(f"  Win rate: {(avg_twelve_hits/avg_dice_rolls)*100:.2f}%")

        if bet_field > 0:
            print(f"\nField bet:")
            print(f"  Average wins per simulation: {avg_field_wins:.1f}")
            if avg_field_wins > 0:
                print(f"  Win frequency: 1 in every {avg_dice_rolls/avg_field_wins:.1f} rolls")
                print(f"  Win rate: {(avg_field_wins/avg_dice_rolls)*100:.2f}%")

### MAIN EXECUTION ###

# Run multiple simulations
if simulation_mode == 'fixed_rounds':
    print(f"Running {num_simulations} simulations of {total_rounds:,} rounds each...")
elif simulation_mode == 'threshold':
    print(f"Running {num_simulations} simulations until win/loss threshold...")
    print(f"  Win threshold: ${win_threshold:+.2f}")
    print(f"  Loss threshold: ${loss_threshold:+.2f}")

final_bankrolls = []
rounds_played_list = []
all_low_hits = []
all_high_hits = []
all_all_hits = []
all_dice_rolls = []
all_twelve_hits = []
all_field_wins = []

for sim in range(num_simulations):
    result = run_single_simulation(sim + 1)
    final_bankrolls.append(result['final_bankroll'])
    rounds_played_list.append(result['rounds_played'])
    all_low_hits.append(result['low_hits'])
    all_high_hits.append(result['high_hits'])
    all_all_hits.append(result['all_hits'])
    all_dice_rolls.append(result['total_dice_rolls'])
    all_twelve_hits.append(result['twelve_hits'])
    all_field_wins.append(result['field_wins'])

    if (sim + 1) % 100 == 0:
        print(f"  Completed {sim + 1}/{num_simulations} simulations...")

### RESULTS ANALYSIS ###

# Calculate statistics on final bankrolls
final_bankrolls.sort()

def percentile(data, perc):
    """Get percentile from sorted data"""
    index = int(len(data) * perc / 100)
    return data[index] if index < len(data) else data[-1]

# Print results summary
print(f"\n=== Craps Simulation Results ===")
print(f"Simulation mode: {simulation_mode}")
print(f"Strategy: {strategy.replace('_', ' ').title()}")
print(f"Number of simulations: {num_simulations}")

if simulation_mode == 'fixed_rounds':
    print(f"Rounds per simulation: {total_rounds:,}")
elif simulation_mode == 'threshold':
    print(f"Win threshold: ${win_threshold:+.2f}")
    print(f"Loss threshold: ${loss_threshold:+.2f}")

print(f"\nBet amounts:")
if bet_pass_line > 0:
    print(f"  Main bet (per round): ${bet_pass_line}")
if bet_odds > 0:
    print(f"  Odds bet (per round when point established): ${bet_odds}")
if bet_field > 0:
    print(f"  Field bet (per dice roll): ${bet_field}")
if bet_twelve > 0:
    print(f"  Twelve bet (per dice roll): ${bet_twelve}")
if bet_low_numbers > 0:
    print(f"  Low numbers side bet (per cycle): ${bet_low_numbers}")
if bet_high_numbers > 0:
    print(f"  High numbers side bet (per cycle): ${bet_high_numbers}")
if bet_all_numbers > 0:
    print(f"  All numbers side bet (per cycle): ${bet_all_numbers}")

# Show bankroll distribution only for fixed_rounds mode
if simulation_mode == 'fixed_rounds':
    print(f"\n=== Final Bankroll Distribution ===")
    print(f"Minimum: ${final_bankrolls[0]:,.2f}")
    print(f"5th Percentile: ${percentile(final_bankrolls, 5):,.2f}")
    print(f"25th Percentile: ${percentile(final_bankrolls, 25):,.2f}")
    print(f"Median (50th): ${percentile(final_bankrolls, 50):,.2f}")
    print(f"Average: ${sum(final_bankrolls)/len(final_bankrolls):,.2f}")
    print(f"75th Percentile: ${percentile(final_bankrolls, 75):,.2f}")
    print(f"95th Percentile: ${percentile(final_bankrolls, 95):,.2f}")
    print(f"Maximum: ${final_bankrolls[-1]:,.2f}")

# Show outcomes
if simulation_mode == 'fixed_rounds':
    positive = sum(1 for b in final_bankrolls if b > 0)
    negative = sum(1 for b in final_bankrolls if b < 0)
    even = sum(1 for b in final_bankrolls if b == 0)
    print(f"\nOutcomes:")
    print(f"  Ended positive: {positive} ({positive/num_simulations*100:.1f}%)")
    print(f"  Ended negative: {negative} ({negative/num_simulations*100:.1f}%)")
    print(f"  Ended even: {even} ({even/num_simulations*100:.1f}%)")
elif simulation_mode == 'threshold':
    wins = sum(1 for b in final_bankrolls if b >= win_threshold)
    losses = sum(1 for b in final_bankrolls if b <= loss_threshold)
    incomplete = num_simulations - wins - losses

    print(f"\n=== Threshold Outcomes ===")
    print(f"  Hit WIN threshold: {wins} ({wins/num_simulations*100:.1f}%)")
    print(f"  Hit LOSS threshold: {losses} ({losses/num_simulations*100:.1f}%)")
    if incomplete > 0:
        print(f"  Incomplete (hit max rounds): {incomplete} ({incomplete/num_simulations*100:.1f}%)")

    # Sort rounds list for percentile calculations
    rounds_played_sorted = sorted(rounds_played_list)
    print(f"\n=== Rounds Until Completion ===")
    print(f"Minimum: {rounds_played_sorted[0]:,}")
    print(f"5th Percentile: {percentile(rounds_played_sorted, 5):,.0f}")
    print(f"25th Percentile: {percentile(rounds_played_sorted, 25):,.0f}")
    print(f"Median: {percentile(rounds_played_sorted, 50):,.0f}")
    print(f"Average: {sum(rounds_played_list)/len(rounds_played_list):,.1f}")
    print(f"75th Percentile: {percentile(rounds_played_sorted, 75):,.0f}")
    print(f"95th Percentile: {percentile(rounds_played_sorted, 95):,.0f}")
    print(f"Maximum: {rounds_played_sorted[-1]:,}")

# Print bet-specific statistics
print_bet_statistics(
    avg_dice_rolls=sum(all_dice_rolls)/num_simulations,
    avg_rounds=sum(rounds_played_list)/num_simulations,
    avg_low_hits=sum(all_low_hits)/num_simulations,
    avg_high_hits=sum(all_high_hits)/num_simulations,
    avg_all_hits=sum(all_all_hits)/num_simulations,
    avg_twelve_hits=sum(all_twelve_hits)/num_simulations,
    avg_field_wins=sum(all_field_wins)/num_simulations
)
