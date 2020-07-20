def save(current_level, current_time):  # in ms
    # read previous scores
    scorefile = open('highscores.txt', 'r+')
    scorelist = scorefile.readlines()
    scorefile.close()
    # check if level already in scores
    exists = None
    previous = None
    for score in scorelist:
        level, time = score.split(': ')
        if level == str(current_level):
            exists = score
            previous = int(time)
    # compare times and update
    if exists:
        if previous > current_time:
            i = scorelist.index(exists)
            scorelist.remove(exists)
            scorelist.insert(i, "{}: {}\n".format(current_level, current_time))
    else:
        scorelist.append("{}: {}\n".format(current_level, current_time))
    # write new scores
    scorefile = open('highscores.txt', 'w+')
    scorefile.writelines(scorelist)
    scorefile.close()
