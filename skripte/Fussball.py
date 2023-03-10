
def n(letter):
  return ord(letter.upper()) - 65

def soccer(team1, team2):
  t1 = list(team1.upper())
  t2 = list(team2.upper())
  win1 = 0
  win2 = 0
  winner = 0
  for i in range(min(len(team1), len(team2))):
    if (n(t1[i]) - n(t2[i])) > 0 and (n(t1[i]) - n(t2[i])) < 13:
      win1 += 1
      # winner = 1
    elif (n(t1[i]) - n(t2[i])) < 0 and (n(t1[i]) - n(t2[i])) > -13:
      win2 += 1
      # winner = 2
    elif (n(t1[i]) - n(t2[i])) > 13:
      win2 += 1
      # winner = 2
    # print(t1[i], n(t1[i]),":", t2[i], n(t2[i]), "=", n(t1[i]) - n(t2[i]), winner )
    # winner = 0
  return win1, win2



def f(contestant1: str, contestant2: str):
    contestant1 = contestant1.lower()
    contestant2 = contestant2.lower()
    len1 = len(contestant1)
    len2 = len(contestant2)
    L = min(len1, len2)
    res1:int = 0
    res2:int =0
    for i in range(L):
        c1 = ord(contestant1[i])
        c2 = ord(contestant2[i])
        diff = c1 - c2
        if diff < 0:
            diff += 26
        diff = diff %26
        if 1 <= diff <= 12:
            res1+=1
        if 14 <= diff <= 25:
            res2+=1
    print(f'{contestant1}:{contestant2}  {res1}:{res2}')
    
soccer = f

# Gruppe A
soccer("Hasenbuck", "Eibach")
soccer("Schweinau", "Langwasser")
soccer("Langwasser", "Hasenbuck")
soccer("Eibach", "Schweinau")
soccer("Hasenbuck", "Schweinau")
soccer("Eibach", "Langwasser")

# Gruppe B
soccer("Sandreuth", "Gostenhof")
soccer("Boxdorf", "Muggenhof")
soccer("Muggenhof", "Sandreuth")
soccer("Gostenhof", "Boxdorf")
soccer("Sandreuth", "Boxdorf")
soccer("Gostenhof", "Muggenhof")

# Gruppe C
soccer("Laufamholz", "Reichelsdorf")
soccer("Gibitzenhof", "Eberhardshof")
soccer("Eberhardshof", "Laufamholz")
soccer("Reichelsdorf", "Gibitzenhof")
soccer("Laufamholz", "Gibitzenhof")
soccer("Reichelsdorf", "Eberhardshof")

# Gruppe D
soccer("Schniegling", "Maxfeld")
soccer("Ziegelstein", "Almoshof")
soccer("Almoshof", "Schniegling")
soccer("Maxfeld", "Ziegelstein")
soccer("Schniegling", "Ziegelstein")
soccer("Maxfeld", "Almoshof")

