import tkinter as tk


def removeLeftRecursion(rulesDiction):
    store = {}
    for lhs in rulesDiction:
        alphaRules = []
        betaRules = []
        allrhs = rulesDiction[lhs]
        for subrhs in allrhs:
            if subrhs[0] == lhs:
                alphaRules.append(subrhs[1:])
            else:
                betaRules.append(subrhs)
        if len(alphaRules) != 0:
            lhs_ = lhs + "'"
            while lhs_ in rulesDiction.keys() or lhs_ in store.keys():
                lhs_ += "'"
            for b in range(0, len(betaRules)):
                betaRules[b].append(lhs_)
            rulesDiction[lhs] = betaRules
            for a in range(0, len(alphaRules)):
                alphaRules[a].append(lhs_)
            alphaRules.append(['#'])
            store[lhs_] = alphaRules
    for left in store:
        rulesDiction[left] = store[left]
    return rulesDiction

def LeftFactoring(rulesDiction):
    newDict = {}
    for lhs in rulesDiction:
        allrhs = rulesDiction[lhs]
        temp = dict()
        for subrhs in allrhs:
            if subrhs[0] not in list(temp.keys()):
                temp[subrhs[0]] = [subrhs]
            else:
                temp[subrhs[0]].append(subrhs)
        new_rule = []
        tempo_dict = {}
        for term_key in temp:
            allStartingWithTermKey = temp[term_key]
            if len(allStartingWithTermKey) > 1:
                lhs_ = lhs + "'"
                while lhs_ in rulesDiction.keys() or lhs_ in tempo_dict.keys():
                    lhs_ += "'"
                new_rule.append([term_key, lhs_])
                ex_rules = []
                for g in temp[term_key]:
                    ex_rules.append(g[1:])
                tempo_dict[lhs_] = ex_rules
            else:
                new_rule.append(allStartingWithTermKey[0])
        newDict[lhs] = new_rule
        for key in tempo_dict:
            newDict[key] = tempo_dict[key]
    return newDict

def first(rule, rules, diction, firsts, term_userdef):
    if len(rule) != 0 and (rule is not None):
        if rule[0] in term_userdef:
            return rule[0]
        elif rule[0] == '#':
            return '#'
    if len(rule) != 0:
        if rule[0] in list(diction.keys()):
            fres = []
            rhs_rules = diction[rule[0]]
            for itr in rhs_rules:
                indivRes = first(itr, rules, diction, firsts, term_userdef)
                if isinstance(indivRes, list):
                    for i in indivRes:
                        fres.append(i)
                else:
                    fres.append(indivRes)
            if '#' not in fres:
                return fres
            else:
                newList = []
                fres.remove('#')
                if len(rule) > 1:
                    ansNew = first(rule[1:], rules, diction, firsts, term_userdef)
                    if ansNew is not None:
                        if isinstance(ansNew, list):
                            newList = fres + ansNew
                        else:
                            newList = fres + [ansNew]
                    else:
                        newList = fres
                    return newList
                fres.append('#')
                return fres

def follow(nt, start_symbol, rules, nonterm_userdef, term_userdef, diction, firsts, follows):
    solset = set()
    if nt == start_symbol:
        solset.add('$')
    for curNT in diction:
        rhs = diction[curNT]
        for subrule in rhs:
            if nt in subrule:
                while nt in subrule:
                    index_nt = subrule.index(nt)
                    subrule = subrule[index_nt + 1:]
                    if len(subrule) != 0:
                        res = first(subrule, rules, diction, firsts,term_userdef)
                        if res is None:  # Check if res is None
                            continue
                        if '#' in res:
                            newList = []
                            res.remove('#')
                            ansNew = follow(curNT, start_symbol, rules, nonterm_userdef, term_userdef, diction, firsts, follows)
                            if ansNew is not None:
                                if isinstance(ansNew, list):
                                    newList = res + ansNew
                                else:
                                    newList = res + [ansNew]
                            else:
                                newList = res
                            res = newList
                    else:
                        if nt != curNT:
                            res = follow(curNT, start_symbol, rules, nonterm_userdef, term_userdef, diction, firsts, follows)
                    if res is not None:
                        if isinstance(res, list):
                            for g in res:
                                solset.add(g)
                        else:
                            solset.add(res)
    return list(solset)

def computeAllFirsts(rules, nonterm_userdef, term_userdef, diction, firsts):
    for rule in rules:
        k = rule.split("->")
        k[0] = k[0].strip()
        k[1] = k[1].strip()
        rhs = k[1]
        multirhs = rhs.split('|')
        for i in range(len(multirhs)):
            multirhs[i] = multirhs[i].strip()
            multirhs[i] = multirhs[i].split()
        diction[k[0]] = multirhs

    print(f"\nRules: \n")
    for y in diction:
        print(f"{y}->{diction[y]}")
    print(f"\nAfter elimination of left recursion:\n")

    diction = removeLeftRecursion(diction)
    for y in diction:
        print(f"{y}->{diction[y]}")
    print("\nAfter left factoring:\n")

    diction = LeftFactoring(diction)
    for y in diction:
        print(f"{y}->{diction[y]}")

    for y in list(diction.keys()):
        t = set()
        for sub in diction.get(y):
            res = first(sub, rules, diction, firsts, term_userdef)  # Pass term_userdef here
            if res is not None:
                if isinstance(res, list):
                    for u in res:
                        t.add(u)
                else:
                    t.add(res)
        firsts[y] = t

    print("\nCalculated firsts: ")
    key_list = list(firsts.keys())
    index = 0
    for gg in firsts:
        print(f"first({key_list[index]}) "
            f"=> {firsts.get(gg)}")
        index += 1

def computeAllFollows(start_symbol, rules, nonterm_userdef, term_userdef, diction, firsts, follows):
    for NT in diction:
        solset = set()
        sol = follow(NT, start_symbol, rules, nonterm_userdef, term_userdef, diction, firsts, follows)
        if sol is not None:
            for g in sol:
                solset.add(g)
        follows[NT] = solset

    print("\nCalculated follows: ")
    key_list = list(follows.keys())
    index = 0
    for gg in follows:
        print(f"follow({key_list[index]})"
            f" => {follows[gg]}")
        index += 1

def createParseTable(diction, firsts, rules, follows, term_userdef):
    import copy
    print("\nFirsts and Follow Result table\n")
    mx_len_first = 0
    mx_len_fol = 0
    for u in diction.keys():
        k1 = len(str(firsts[u]))
        k2 = len(str(follows[u]))  # Use u instead of 'u'

        if k1 > mx_len_first:
            mx_len_first = k1
        if k2 > mx_len_fol:
            mx_len_fol = k2

    print(f"{{:<{10}}} "
          f"{{:<{mx_len_first + 5}}} "
          f"{{:<{mx_len_fol + 5}}}"
          .format("Non-T", "FIRST", "FOLLOW"))
    for u in diction:
        print(f"{{:<{10}}} "
              f"{{:<{mx_len_first + 5}}} "
              f"{{:<{mx_len_fol + 5}}}"
              .format(u, str(firsts[u]), str(follows[u])))

    ntlist = list(diction.keys())
    terminals = copy.deepcopy(term_userdef)
    terminals.append('$')

    mat = []
    for x in diction:
        row = []
        for y in terminals:
            row.append('')

        mat.append(row)

    grammar_is_LL = True

    for lhs in diction:
        rhs = diction[lhs]
        for y in rhs:
            res = first(y, rules, diction, firsts, term_userdef)

            if res is None: 
                continue

            if '#' in res:
                if isinstance(res, str):
                    firstFollow = []
                    fol_op = follows[lhs]
                    if fol_op is str:
                        firstFollow.append(fol_op)
                    else:
                        for u in fol_op:
                            firstFollow.append(u)
                    res = firstFollow
                else:
                    res.remove('#')
                    res = list(res) + list(follows[lhs])
            ttemp = []
            if isinstance(res, str):
                ttemp.append(res)
                res = copy.deepcopy(ttemp)
            for c in res:
                print("Current c:", c)  # Debugging print statement
                if c is not None:
                    xnt = ntlist.index(lhs)
                    yt = terminals.index(c)
                    if mat[xnt][yt] == '':
                        mat[xnt][yt] = mat[xnt][yt] \
                                       + f"{lhs}->{' '.join(y)}"
                    else:
                        if f"{lhs}->{y}" in mat[xnt][yt]:
                            continue
                        else:
                            grammar_is_LL = False
                            mat[xnt][yt] = mat[xnt][yt] \
                                           + f",{lhs}->{' '.join(y)}"

    print("\nGenerated parsing table:\n")
    frmt = "{:>12}" * len(terminals)
    print(frmt.format(*terminals))

    j = 0
    for y in mat:
        frmt1 = "{:>12}" * len(y)
        print(f"{ntlist[j]} {frmt1.format(*y)}")
        j += 1

    return (mat, grammar_is_LL, terminals)


def validateStringUsingStackBuffer(parsing_table, grammarll1, table_term_list, input_string, term_userdef, start_symbol, diction, rules):
    print(f"\nValidate String => {input_string}\n")
    if grammarll1 == False:
        return f"\nInput String = " \
            f"\"{input_string}\"\n" \
            f"Grammar is not LL(1)"

    stack = [start_symbol, '$']
    buffer = []

    input_string = input_string.split()
    input_string.reverse()
    buffer = ['$'] + input_string

    print("{:>20} {:>20} {:>20}".
        format("Buffer", "Stack","Action"))

    while True:
        if stack == ['$'] and buffer == ['$']:
            print("{:>20} {:>20} {:>20}"
                .format(' '.join(buffer),
                        ' '.join(stack),
                        "Valid"))
            return "\nValid String!"
        elif stack[0] not in term_userdef:
            x = list(diction.keys()).index(stack[0])
            y = table_term_list.index(buffer[-1])
            if parsing_table[x][y] != '':
                entry = parsing_table[x][y]
                print("{:>20} {:>20} {:>25}".
                    format(' '.join(buffer),
                            ' '.join(stack),
                            f"T[{stack[0]}][{buffer[-1]}] = {entry}"))
                lhs_rhs = entry.split("->")
                lhs_rhs[1] = lhs_rhs[1].replace('#', '').strip()
                entryrhs = lhs_rhs[1].split()
                stack = entryrhs + stack[1:]
            else:
                return f"\nInvalid String! No rule at " \
                    f"Table[{stack[0]}][{buffer[-1]}]."
        else:
            if stack[0] == buffer[-1]:
                print("{:>20} {:>20} {:>20}"
                    .format(' '.join(buffer),
                            ' '.join(stack),
                            f"Matched:{stack[0]}"))
                buffer = buffer[:-1]
                stack = stack[1:]
            else:
                return "\nInvalid String! " \
                    "Unmatched terminal symbols"


def parse_input():
    rules_input = rules_text.get("1.0", tk.END).strip().split("\n")
    nonterm_userdef_input = nonterm_text.get().strip().split(",")
    term_userdef_input = term_text.get().strip().split(",")
    sample_input_string_input = sample_input_text.get().strip()

    diction = {}
    firsts = {}
    follows = {}

    computeAllFirsts(rules_input, nonterm_userdef_input, term_userdef_input, diction, firsts)
    start_symbol = list(diction.keys())[0]
    computeAllFollows(start_symbol, rules_input, nonterm_userdef_input, term_userdef_input, diction, firsts, follows)
    (parsing_table, result, tabTerm) = createParseTable(diction, firsts, rules_input, follows, term_userdef_input)
    if sample_input_string_input != "":
        validity = validateStringUsingStackBuffer(parsing_table, result, tabTerm, sample_input_string_input, term_userdef_input, start_symbol, diction, rules_input)
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, validity)


root = tk.Tk()
root.title("LL Parser")

rules_label = tk.Label(root, text="Rules:")
rules_label.grid(row=0, column=0, sticky="w")
rules_text = tk.Text(root, height=6, width=50)
rules_text.grid(row=0, column=1)

nonterm_label = tk.Label(root, text="Nonterminal User Definition:")
nonterm_label.grid(row=1, column=0, sticky="w")
nonterm_text = tk.Entry(root)
nonterm_text.grid(row=1, column=1)

term_label = tk.Label(root, text="Terminal User Definition:")
term_label.grid(row=2, column=0, sticky="w")
term_text = tk.Entry(root)
term_text.grid(row=2, column=1)

sample_input_label = tk.Label(root, text="Sample Input String:")
sample_input_label.grid(row=3, column=0, sticky="w")
sample_input_text = tk.Entry(root)
sample_input_text.grid(row=3, column=1)

submit_button = tk.Button(root, text="Submit", command=parse_input)
submit_button.grid(row=4, column=1)

result_label = tk.Label(root, text="Result:")
result_label.grid(row=5, column=0, sticky="w")
result_text = tk.Text(root, height=6, width=50)
result_text.grid(row=5, column=1)

root.mainloop()
