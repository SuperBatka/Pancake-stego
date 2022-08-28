import random
from pydub import AudioSegment

def soundAnalisis(inputSound,size):
    sound = inputSound[:]
    mono_list = sound.split_to_mono()
    Chanel0 = mono_list[0]
    Chanel1 = mono_list[1]
    pos_list =[]
    lis = []
    left_list=[]
    count1 = 0
    count = 0
    count3 = 0
    count4 = 0
    count5 = 0
    count6 = 0
    countCRCbit = 0
    while len(Chanel0)>0:
        slice0 = Chanel0[:size]
        slice1 = Chanel1[:size]
        left_list.append(slice0)
        Chanel0 = Chanel0[size:]
        Chanel1 = Chanel1[size:]
        count1+=1

        if abs(slice0.max_dBFS - slice1.max_dBFS)<0.005 and count1 < len(sound)/size and slice0.max_dBFS > -60 and slice1.max_dBFS > -60:
            count+=1
            count3 += 1
            lis.append(1)
            if count6 == 0:
                count6 = count1
        else:
            if count3 > 37:
                count4+= count3
                countCRCbit += count3 //8
                count5+=1
                pos_list.append(list([count6-1,count1-1]))
            count6 = 0
            count3 = 0
            lis.append(0)
    #print(pos_list)
    print("max amount of bits {}".format(count4 - len(pos_list)* 17 - countCRCbit))
    return pos_list , count4 - len(pos_list)* 17 - countCRCbit



def encodeMessage(bit_lists, inputSound, size,pos_list):

    stop_bits = "10010001"
    sound = inputSound[:]
    copy_sound = sound[:]

    flag = 0
    count7 = 0
    new_sound =[]
    count8 = 0
    stop_counter = 0
    start = True
    stop = False
    end = False
    stop_end = False
    i = 0
    bitSum = 0
    while i < (len(sound)//size):
        if i in range(pos_list[count7][0], pos_list[count7][1]):
            flag = 1
            if (count8)%8 == 0:
                if ((i+7) <= pos_list[count7][1]) and ((i + 16) > pos_list[count7][1]) and not start:
                    stop = True
            
            if start and not end:                     # если начало промежутка, то вставляем 1
                new_sound.append(1)
                new_sound.append(1)
                i+=1
                start = False             

            elif stop and not end:
                while stop_counter < len(stop_bits):
                    new_sound.append( int(stop_bits[stop_counter]) )
                    stop_counter += 1
                    i+=1
                    if stop_counter >= len(stop_bits) and stop_end:
                        end = True
                #--------------------------------------
                else:
                    new_sound.append( 0 ) #3
                
            elif end:
                new_sound.append( 0 ) #7

            else:
                #------------------------------------------
                if count8 < len(bit_lists):
                    for j in range(8):
                        new_sound.append( int(bit_lists[count8]))                                     #если всё хорошо, то пишем наше сообщение
                        bitSum ^= int(bit_lists[count8])
                        count8 += 1
                        #i+= 1
                    new_sound.append(bitSum)
                    i+=7
                    i+=1
                    bitSum = 0                   
                    if count8 >= len(bit_lists):
                            stop = True
                            stop_end = True
                #-------------------------------------------
                else:                                                                               #если сообщение закончилось, то закидываем нулями
                    new_sound.append(0)

        else:                                                                          #если не попали в промежуток, то всё обращаем в исходное
            new_sound.append(0)
            if flag == 1 and count7<(len(pos_list)-1):
                count7 += 1
            flag = 0
            stop_counter = 0
            #ByteSum = 0
            start = True #ждём старт
            stop = False #не записываем стоп
        i+=1


    #print(new_sound)
    #input("continue?")


    slices_list = []
    count1 = 0
    while len(copy_sound)>0:
        if count1 <len(new_sound) and new_sound[count1] == 0:
            slices_temp = copy_sound[:size]
            tmpchk = slices_temp.split_to_mono()
            if abs(tmpchk[0].max_dBFS -tmpchk[1].max_dBFS) < 0.005:
                rn = random.choice([-1, 1])
                #slices = slices_temp.pan(+0.01)
                slices = slices_temp.apply_gain_stereo(+0.06 * rn,-0.06 * rn)
            else:
                slices = slices_temp[:]
            #tmpchk = slices.split_to_mono()
        else:
            slices = copy_sound[:size]
        slices_list.append(slices)
        copy_sound = copy_sound[size:]
        count1+=1
        
    newS = slices_list[0]
    count2 = 1
    for i in range(1,count1):
        chunk = slices_list[i]
        newS+=chunk
        count2+=1
    #print(len(newS))
    return newS[:]

def extender(inputSound, size):
    sound = inputSound[:]
    mono_list = sound.split_to_mono()
    Chanel0 = mono_list[0]
    Chanel1 = mono_list[1]
    count1 = 0
    slices_list = []

    while len(Chanel0)>0:
        slice0 = Chanel0[:size]
        slice1 = Chanel1[:size]
        Chanel0 = Chanel0[size:]
        Chanel1 = Chanel1[size:]
        count1+=1
        if slice0.max_dBFS != slice1.max_dBFS and abs(slice0.max_dBFS - slice1.max_dBFS) < 5 and slice0.max_dBFS > -60 and slice1.max_dBFS > -60:
            db_diff =slice0.max_dBFS - slice1.max_dBFS
            if db_diff > 0:
                slice0=slice0.apply_gain(-db_diff)
            else:
                slice1 = slice1.apply_gain(db_diff)      
        slices_list.append(AudioSegment.from_mono_audiosegments(slice0, slice1)) 

    newS = slices_list[0]
    count2 = 1
    for i in range(1,count1):
        chunk = slices_list[i]
        newS+=chunk
        count2+=1
    return newS[:]

def encodeMenu():
    positionDict = {}
    bitsAmountDict ={}
    print("Введите имя входного файла")
    filename = input("> ")
    try:
        inputSound = AudioSegment.from_wav(filename)
    except:
        print("Такого файла не существует")
        return
    print("Воспользоваться алгоритмом, для увелечения количество информации, которую можно будет передать? Может ухудшить качество выходной записи. \n 1 - Да, 0 - Нет")
    extenderIs = input("> ")
   
    while(True):
        tempSound = inputSound[:]
        print("Выберете длительность интервала от 100 до 500")
        size = int(input("> "))
        if int(extenderIs):
            tempSound = extender(tempSound,size)
        positionDict[size], bitsAmountDict[size] = soundAnalisis(tempSound,size)
        #print (positionDict)
        print("1 - продолжить, 2 -выбрать другой интервал, 0 - вернуться в меню")
        choice = int(input("> "))
        if choice == 0:
            return
        if (choice == 1):
            inputSound = tempSound[:]
            break
    position_list = positionDict[size]
    bitsAmount = bitsAmountDict[size]
    while(True):
        print("Введите строку, которую хотите спрятать")
        stringToHide = input("> ")
        bytesToHide = stringToHide.encode("utf-8")
        bitsList = []
        for i in bytesToHide:
            bitsList.append(bin(i).lstrip("0b").zfill(8))
        resultBitList = "".join(bitsList)
        if bitsAmount > len(resultBitList):
            break
        print("Ваше сообщение слишком большое для данного контейнера")
        print("Вы должны уменьшить ваше сообщение минимум на {} байт".format(len(resultBitList)//8 - bitsAmount//8))
        print("1 - поменять сообщение, 0 - выйти в меню")
        choice = int(input("> "))
        if choice == 0:
            return
    print("Введите имя выходного файла")
    outputFilename  = input("> ")
    encodedSound = encodeMessage(resultBitList, inputSound, size, position_list)
    try:
        check = decodeMessage(encodedSound, size)
    except:
        print("Не получилось однозначно спрятать сообщение. Попробуйте повторить процедуру с другими параметрами")
        return
    #check = decodeMessage(encodedSound, size)
    if (check == stringToHide):
        encodedSound.export(outputFilename, format="wav", bitrate = "999k")
        print("Сообщение успешно спрятано")
    else:
        print("Не получилось однозначно спрятать сообщение. Попробуйте повторить процедуру с другими параметрами")
        return

def decodeMessage(inputSound, size):
    panned = inputSound[:]
    mono_list = panned.split_to_mono()

    Chanel0 = mono_list[0]
    Chanel1 = mono_list[1]

    bit_list =[]
    slice0 = 0
    slice1 = 0
    count1 = 0
    while len(Chanel0)>0:
        slice0 = Chanel0[:size]
        slice1 = Chanel1[:size]
        Chanel0 = Chanel0[size:]
        Chanel1 = Chanel1[size:]
        count1+=1
        if abs(slice0.max_dBFS - slice1.max_dBFS)<0.005 and slice0.max_dBFS > -60 and slice1.max_dBFS > -60:
            bit_list.append(1) #for new pan
        else:
            bit_list.append(0) #for new pan

    #print(bit_list) #todo remove
    #print("".join(map(str,bit_list)))
    result_bit_str =""

    start = False
    stop = False
    byteSum = 0
    Alert = False

    bit_counter = 0
    i = 0
    while i < len(bit_list)-1:
        if int(bit_list[i]) and int(bit_list[i+1]) and not start:
            i+=2
            start = True
            continue
        if start:
            result_bit_str += str(bit_list[i]) 
            bit_counter += 1

            if bit_counter == 8:
                temp_8_bit  = result_bit_str[-8:]
                bit_counter = 0
                
                #print(result_bit_str[-8:]) #todo remove
                if temp_8_bit == "10010001":
                    result_bit_str = result_bit_str[:-8]
                    start = False
                else:
                    for j in list(temp_8_bit):
                        byteSum ^= int(j)
                    if  byteSum != int(bit_list[i+1]):
                        Alert = True
                        #print("byteSum = {}, bit = {}".format(byteSum,int(bit_list[i+1]) )) #todo remove
                    byteSum = 0
                    i+=1
        i+=1
    n = int (result_bit_str,2)
    s = n.to_bytes((n.bit_length() + 7) // 8, 'big').decode()
    #print (s)
    if Alert:
        s += "\n -----------------\n ВНИМАНИЕ! возможно на контейнер было осуществленно внешнее воздействие! \n -----------------"
    return s

def decodeMenu():
    print("Введите имя входного файла")
    filename = input("> ")
    try:
        inputSound = AudioSegment.from_wav(filename)
    except:
        print("Такого файла не существует")
        return
    while(True):
        print("Выберете длительность интервала от 100 до 500")
        size = int(input("> "))
        try:
            result = decodeMessage(inputSound, size)
        except:
            print("Данный контейнер пустой")
            print("1 - выбрать другой интервал, 0 - вернуться в меню")
            choice = int(input())
            if choice == 0:
                return
        else:
            print(result)
            return



if __name__ == '__main__':
    print("Стеганопроект Pancake \n")
    while(True):
        print("1 - спрятать сообщение, 2 - прочитать сообщение из контейнера, 0 - выйти")
        choice = input("> ")
        if int(choice) == 1:
            encodeMenu()
        if int(choice) == 2:
            decodeMenu()
        if int(choice) == 0:
            break

            
