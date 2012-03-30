
def test_func(emitt):    
    flag_1 = False
    if flag_1: # pragma: no cond(T)
        emit('flag_1 T')
    
    for flag_2 in [True, False]:
        if flag_2 and flag_1: # pragma: no cond(T T,F T)
            emit('flag_2 and flag_1 T T')
