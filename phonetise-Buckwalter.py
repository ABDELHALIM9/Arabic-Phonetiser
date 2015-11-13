#!/usr/bin/python
# -*- coding: UTF8 -*-

import sys
import codecs
import re
import os

buckwalter = { #mapping from Arabic script to Buckwalter
	u'\u0628': u'b' , u'\u0630': u'*' , u'\u0637': u'T' , u'\u0645': u'm',
	u'\u062a': u't' , u'\u0631': u'r' , u'\u0638': u'Z' , u'\u0646': u'n',
	u'\u062b': u'^' , u'\u0632': u'z' , u'\u0639': u'E' , u'\u0647': u'h',
	u'\u062c': u'j' , u'\u0633': u's' , u'\u063a': u'g' , u'\u062d': u'H',
	u'\u0642': u'q' , u'\u0641': u'f' , u'\u062e': u'x' , u'\u0635': u'S',
	u'\u0634': u'$' , u'\u062f': u'd' , u'\u0636': u'D' , u'\u0643': u'k',
	u'\u0623': u'>' , u'\u0621': u'\'', u'\u0626': u'}' , u'\u0624': u'&',
	u'\u0625': u'<' , u'\u0622': u'|' , u'\u0627': u'A' , u'\u0649': u'Y',
	u'\u0629': u'p' , u'\u064a': u'y' , u'\u0644': u'l' , u'\u0648': u'w',
	u'\u064b': u'F' , u'\u064c': u'N' , u'\u064d': u'K' , u'\u064e': u'a',
	u'\u064f': u'u' , u'\u0650': u'i' , u'\u0651': u'~' , u'\u0652': u'o'
}

ArabicScript = { #mapping from Buckwalter to Arabic script
	u'b': u'\u0628' , u'*': u'\u0630' , u'T': u'\u0637' , u'm': u'\u0645',
	u't': u'\u062a' , u'r': u'\u0631' , u'Z': u'\u0638' , u'n': u'\u0646',
	u'^': u'\u062b' , u'z': u'\u0632' , u'E': u'\u0639' , u'h': u'\u0647',
	u'j': u'\u062c' , u's': u'\u0633' , u'g': u'\u063a' , u'H': u'\u062d',
	u'q': u'\u0642' , u'f': u'\u0641' , u'x': u'\u062e' , u'S': u'\u0635',
	u'$': u'\u0634' , u'd': u'\u062f' , u'D': u'\u0636' , u'k': u'\u0643',
	u'>': u'\u0623' , u'\'': u'\u0621', u'}': u'\u0626' , u'&': u'\u0624',
	u'<': u'\u0625' , u'|': u'\u0622' , u'A': u'\u0627' , u'Y': u'\u0649',
	u'p': u'\u0629' , u'y': u'\u064a' , u'l': u'\u0644' , u'w': u'\u0648',
	u'F': u'\u064b' , u'N': u'\u064c' , u'K': u'\u064d' , u'a': u'\u064e',
	u'u': u'\u064f' , u'i': u'\u0650' , u'~': u'\u0651' , u'o': u'\u0652'
}

def arabicToBuckwalter(word): #Convert input string to Buckwalter
	res = ''
	for letter in word:
		if(letter in buckwalter):
			res += buckwalter[letter]
		else:
			res += letter
	return res

def buckwalterToArabic(word): #Convert input string to Arabic
	res = ''
	for letter in word:
		if(letter in ArabicScript):
			res += ArabicScript[letter]
		else:
			res += letter
	return res

#----------------------------------------------------------------------------
#Grapheme to Phoneme mappings------------------------------------------------
#----------------------------------------------------------------------------
unambiguousConsonantMap = {
	u'b': u'b' , u'*': u'*' , u'T': u'T' , u'm': u'm' ,
	u't': u't' , u'r': u'r' , u'Z': u'Z' , u'n': u'n' ,
	u'^': u'^' , u'z': u'z' , u'E': u'E' , u'h': u'h' ,
	u'j': u'j' , u's': u's' , u'g': u'g' , u'H': u'H' ,
	u'q': u'q' , u'f': u'f' , u'x': u'x' , u'S': u'S' ,
	u'$': u'$' , u'd': u'd' , u'D': u'D' , u'k': u'k' ,
	u'>': u'<' , u'\'': u'<' , u'}': u'<' , u'&': u'<' ,
	u'<': u'<'
}

ambiguousConsonantMap = {
	u'l': [u'l', u''], u'w': u'w', u'y': u'y', u'p': [u't', u''] #These consonants are only unambiguous in certain contexts
}

maddaMap = {
	u'|': [[u'<', u'aa'], [u'<', u'AA']]
}

vowelMap = {
	u'A': [[u'aa', u''], [u'AA', u'']], u'Y': [[u'aa', u''], [u'AA', u'']],
	u'w': [[u'uu0', u'uu1'], [u'UU0', u'UU1']],
	u'y': [[u'ii0', u'ii1'], [u'II0', u'II1']],
	u'a': [u'a', u'A'],
	u'u': [[u'u0', u'u1'], [u'U0', u'U1']],
	u'i': [[u'i0', u'i1'], [u'I0', u'I1']],
}

nunationMap = {
	u'F': [[u'a', u'n'], [u'A', u'n']], u'N':[[u'u1', u'n'], [u'U1', u'n']], u'K': [[u'i1', u'n'], [u'I1', u'n']]
}

diacritics = [u'o', u'a', u'u', u'i', u'F', u'N', u'K', u'~']
diacriticsWithoutShadda = [u'o', u'a', u'u', u'i', u'F', u'N', u'K']
emphatics = [u'D', u'S', u'T', u'Z', u'g', u'x', u'q']
forwardEmphatics = [u'g', u'x']
consonants = [u'>', u'<', u'}', u'&', u'\'', u'b', u't', u'^', u'j', u'H', u'x', u'd', u'*', u'r', u'z', u's', u'$', u'S', u'D', u'T', u'Z', u'E', u'g', u'f', u'q', u'k', u'l', u'm', u'n', u'h', u'|']

#------------------------------------------------------------------------------------
#Words with fixed irregular pronunciations-------------------------------------------
#------------------------------------------------------------------------------------
fixedWords = {
	u'h*A': [u'h aa * aa', u'h aa * a',],
	u'h*h': [u'h aa * i0 h i0', u'h aa * i1 h'],
	u'h*An': [u'h aa * aa n i0', u'h aa * aa n'],
	u'h&lA\'': [u'h aa < u0 l aa < i0', u'h aa < u0 l aa <'],
	u'*lk': [u'* aa l i0 k a', u'* aa l i0 k'],
	u'k*lk': [u'k a * aa l i0 k a', u'k a * aa l i1 k'],
	u'*lkm': u'* aa l i0 k u1 m',
	u'>wl}k': [u'< u0 l aa < i0 k a', u'< u0 l aa < i1 k'],
	u'Th': u'T aa h a',
	u'lkn': [u'l aa k i0 nn a', u'l aa k i1 n'],
	u'lknh': u'l aa k i0 nn a h u0',
	u'lknhm': u'l aa k i0 nn a h u1 m',
	u'lknk': [u'l aa k i0 nn a k a', u'l aa k i0 nn a k i0'],
	u'lknkm': u'l aa k i0 nn a k u1 m',
	u'lknkmA': u'l aa k i0 nn a k u0 m aa',
	u'lknnA': u'l aa k i0 nn a n aa',
	u'AlrHmn': [u'rr a H m aa n i0',  u'rr a H m aa n'],
	u'Allh': [u'll aa h i0', u'll aa h', u'll AA h u0', u'll AA h a', u'll AA h', u'll A'],
	u'h*yn': [u'h aa * a y n i0', u'h aa * a y n'],

	u'nt': u'n i1 t',
	u'fydyw': u'v i0 d y uu1',
	u'lndn': u'l A n d u1 n'
}

def isFixedWord(word, results, orthography, pronunciations):
	lastLetter = ''
	if(len(word) > 0):
		lastLetter = word[-1]
	if(lastLetter == u'a'):
		lastLetter = [u'a', u'A']
	elif(lastLetter == u'A'):
		lastLetter = [u'aa']
	elif(lastLetter == u'u'):
		lastLetter = [u'u0']
	elif(lastLetter == u'i'):
		lastLetter = [u'i0']
	elif(lastLetter in unambiguousConsonantMap):
		lastLetter = [unambiguousConsonantMap[lastLetter]]
	wordConsonants = re.sub(u'[^h*Ahn\'>wl}kmyTtfd]', '', word) #Remove all dacritics from word
	if(wordConsonants in fixedWords): #check if word is in the fixed word lookup table
		if(isinstance(fixedWords[wordConsonants], list)):
			for pronunciation in fixedWords[wordConsonants]:
				if(pronunciation.split(' ')[-1] in lastLetter):
					results += word + ' ' + pronunciation + '\n' #add each pronunciation to the pronunciation dictionary
					pronunciations.append(pronunciation.split(' '))
		else:
			results += word + ' ' + fixedWords[wordConsonants] + '\n' #add pronunciation to the pronunciation dictionary
			pronunciations.append(fixedWords[wordConsonants].split(' '))
	return results

#-----------------------------------------------------------------------------------------------------
#Read input file--------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------
try:
	inputFileName = sys.argv[1]
except:
	print("No input file provided")
	sys.exit()

inputFile = codecs.open(inputFileName, 'r', 'utf-8')
utterances = inputFile.read().splitlines()
inputFile.close()

result = '' #Pronunciations Dictionary
utterancesPronuncations = [] #Most likely pronunciation for all utterances

#-----------------------------------------------------------------------------------------------------
#Loop through utterances------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------
utteranceNumber = 1
for utterance in utterances:
	wavFileName = ''
	try:
		wavFileName = utterance.split(' "')[0].rstrip() #Split line and get file name from first part
		utterance = " ".join(utterance.split(' "')[1:]).strip('"').rstrip() #Split line and get the orthography from the second part
	except:
		print("Format Error in utterance number " + str(utteranceNumber))
		sys.exit()

	utteranceNumber += 1
	utterancesPronuncations.append('') # Add empty entry that will hold this utterance's pronuncation

	#Do some normalisation work and split utterance to words
	utterance = utterance.replace(u'AF', u'F')
	utterance = utterance.replace(u'\u0640', u'')
	utterance = utterance.replace(u'o', u'')
	utterance = utterance.replace(u'aA', u'A')
	utterance = utterance.replace(u'aY', u'Y')
	utterance = utterance.replace(u' A', u' ')
	utterance = utterance.replace(u'F', u'an')
	utterance = utterance.replace(u'N', u'un')
	utterance = utterance.replace(u'K', u'in')
	utterance = utterance.replace(u'|', u'>A')
	utterance = utterance.split(u' ')
	
	#Deal with Hamza types that when not followed by a short vowel letter,
	#this short vowel is added automatically
	utterance = re.sub(u'Ai', u'<i', utterance)
	utterance = re.sub(u'Aa', u'>a', utterance)
	utterance = re.sub(u'Au', u'>u', utterance)
	utterance = re.sub(u'^>([^auAw])', u'>a\\1', utterance)
	utterance = re.sub(u' >([^auAw ])', u' >a\\1', utterance)
	utterance = re.sub(u'<([^i])', u'<i\\1', utterance)
	if(utteranceNumber < 3):
		print utterance
	#---------------------------
	wordIndex = -1
	
	#Loop through words
	for word in utterance:
		wordIndex += 1
		if(not word in ['-', 'sil']):
			pronunciations = [] #Start with empty set of possible pronunciations of current word
			result = isFixedWord(word, result, word, pronunciations) #Add fixed irregular pronuncations if possible

			emphaticContext = False #Indicates whether current character is in an emphatic context or not. Starts with False
			word = u'bb' + word + u'ee' #This is the end/beginning of word symbol. just for convenience

			phones = [] #Empty list which will hold individual possible word's pronunciation

			#-----------------------------------------------------------------------------------
			#MAIN LOOP: here is where the Modern Standard Arabic phonetisation rule-set starts--
			#-----------------------------------------------------------------------------------
			for index in range(2, len(word) - 2):
				letter = word[index] #Current Character
				letter1 = word[index + 1] #Next Character
				letter2 = word[index + 2] #Next-Next Character
				letter_1 = word[index - 1] #Previous Character
				letter_2 = word[index - 2] #Before Previous Character
				#----------------------------------------------------------------------------------------------------------------
				if(letter in consonants + [u'w', u'y'] and not letter in emphatics + [u'r'""", u'l'"""]): #non-emphatic consonants (except for Lam and Ra) change emphasis back to False
					emphaticContext = False
				if(letter in emphatics): #Emphatic consonants change emphasis context to True
					emphaticContext = True
				if(letter1 in emphatics and not letter1 in forwardEmphatics): #If following letter is backward emphatic, emphasis state is set to True
					emphaticContext = True
				#----------------------------------------------------------------------------------------------------------------
				#----------------------------------------------------------------------------------------------------------------
				if(letter in unambiguousConsonantMap): #Unambiguous consonant phones. These map to a predetermined phoneme
					phones += [unambiguousConsonantMap[letter]]
				#----------------------------------------------------------------------------------------------------------------
				if(letter == u'l'): #Lam is a consonant which requires special treatment
					if((not letter1 in diacritics and not letter1 in vowelMap) and letter2 in [u'~']):#Lam could be omitted in definite article (sun letters)
						phones += [ambiguousConsonantMap[u'l'][1]] #omit
					else:
						phones += [ambiguousConsonantMap[u'l'][0]] #do not omit
				#----------------------------------------------------------------------------------------------------------------
				if(letter == u'~' and not letter_1 in [u'w', u'y'] and len(phones) > 0):#shadda just doubles the letter before it 
					phones[-1] += phones[-1]
				#----------------------------------------------------------------------------------------------------------------
				if(letter == u'|'): #Madda only changes based in emphaticness
					if(emphaticContext):
						phones += [maddaMap[u'|'][1]]
					else:
						phones += [maddaMap[u'|'][0]]
				#----------------------------------------------------------------------------------------------------------------
				if(letter == u'p'): #Ta' marboota is determined by the following if it is a diacritic or not
					if(letter1 in diacritics):
						phones += [ambiguousConsonantMap[u'p'][0]]
					else:
						phones += [ambiguousConsonantMap[u'p'][1]]
				#----------------------------------------------------------------------------------------------------------------
				if(letter in vowelMap):
					if(letter in [u'w', u'y']): #Waw and Ya are complex they could be consonants or vowels and their gemination is complex as it could be a combination of a vowel and consonants
						if(letter1 in diacriticsWithoutShadda + [u'A', u'Y'] or (letter1 in [u'w', u'y'] and not letter2 in diacritics + [u'A', u'w', u'y']) or (letter_1 in diacriticsWithoutShadda and letter1 in consonants + [u'e'])):
							if((letter in [u'w'] and letter_1 in [u'u'] and not letter1 in [u'a', u'i', u'A', u'Y']) or (letter in [u'y'] and letter_1 in [u'i'] and not letter1 in [u'a', u'u', u'A', u'Y'])):
								if(emphaticContext):
									phones += [vowelMap[letter][1][0]]
								else:
									phones += [vowelMap[letter][0][0]]
							else:
								if(letter1 in [u'A'] and letter in [u'w'] and letter2 in [u'e']):
									phones += [[ambiguousConsonantMap[letter], vowelMap[letter][0][0]]]
								else:
									phones += [ambiguousConsonantMap[letter]]
						elif(letter1 in [u'~']):
							if(letter_1 in [u'a'] or (letter in [u'w'] and letter_1 in [u'i', u'y']) or (letter in [u'y'] and letter_1 in [u'w', u'u'])):
								phones += [ambiguousConsonantMap[letter], ambiguousConsonantMap[letter]]
							else:
								phones += [vowelMap[letter][0][0], ambiguousConsonantMap[letter]]
						else: #Waws and Ya's at the end of the word could be shortened
							if(emphaticContext):
								if(letter_1 in consonants + [u'u', u'i'] and letter1 in [u'e']):
									phones += [[vowelMap[letter][1][0], vowelMap[letter][1][0][1:]]]
								else:
									phones += [vowelMap[letter][1][0]]
							else:
								if(letter_1 in consonants + [u'u', u'i'] and letter1 in [u'e']):
									phones += [[vowelMap[letter][0][0], vowelMap[letter][0][0][1:]]]
								else:
									phones += [vowelMap[letter][0][0]]
					if(letter in [u'u', u'i']): #Kasra and Damma could be mildened if before a final silent consonant
						if(emphaticContext):
							if((letter1 in unambiguousConsonantMap or letter1 == u'l') and letter2 == u'e' and len(word) > 7):
								phones += [vowelMap[letter][1][1]]
							else:
								phones += [vowelMap[letter][1][0]]
						else:
							if((letter1 in unambiguousConsonantMap or letter1 == u'l') and letter2 == u'e' and len(word) > 7):
								phones += [vowelMap[letter][0][1]]
							else:
								phones += [vowelMap[letter][0][0]]
					if(letter in [u'a', u'A', u'Y']): #Alif could be ommited in definite article and beginning of some words
						if(letter in [u'A'] and letter_1 in [u'w', u'k'] and letter_2 == u'b'):
							phones += [[u'a', vowelMap[letter][0][0]]]
						elif(letter in [u'A'] and letter_1 in [u'u', u'i']):
							temp = True #do nothing
						elif(letter in [u'A'] and letter_1 in [u'w'] and letter1 in [u'e']): #Waw al jama3a: The Alif after is optional
							phones += [[vowelMap[letter][0][0], vowelMap[letter][0][1]]]
						elif(letter in [u'A', u'Y'] and letter1 in [u'e']):
							if(emphaticContext):
								phones += [[vowelMap[letter][1][0], vowelMap[u'a'][1]]]
							else:
								phones += [[vowelMap[letter][0][0], vowelMap[u'a'][0]]]
						else:
							if(emphaticContext):
								phones += [vowelMap[letter][1][0]]
							else:
								phones += [vowelMap[letter][0][0]]
			#-------------------------------------------------------------------------------------------------------------------------
			#End of main loop---------------------------------------------------------------------------------------------------------
			#-------------------------------------------------------------------------------------------------------------------------
			possibilities = 1 #Holds the number of possible pronunciations of a word

			#count the number of possible pronunciations
			for letter in phones:
				if(isinstance(letter, list)):
					possibilities = possibilities * len(letter)
		
			#Generate all possible pronunciations
			for i in range(0, possibilities):
				pronunciations.append([])
				iterations = 1
				for index, letter in enumerate(phones):
					if(isinstance(letter, list)):
						curIndex = (i / iterations) % len(letter)
						if(letter[curIndex] != u''):
							pronunciations[-1].append(letter[curIndex])
						iterations = iterations * len(letter)
					else:
						if(letter != u''):
							pronunciations[-1].append(letter)

			#Iterate through each pronunciation to perform some house keeping. And append pronunciation to dictionary
			# 1- Remove duplicate vowels
			# 2- Remove duplicate y and w
			for pronunciation in pronunciations:
				prevLetter = ''
				toDelete = []
				for i in range(0, len(pronunciation)):
					letter = pronunciation[i]
					if(letter in ['aa', 'uu0', 'ii0', 'AA', 'UU0', 'II0'] and prevLetter.lower() == letter[1:].lower()):#Delete duplicate consecutive vowels
						toDelete.append(i - 1)
						pronunciation[i] = pronunciation[i - 1][0] + pronunciation[i - 1]
					if(letter in ['u0', 'i0'] and prevLetter.lower() == letter.lower()):#Delete duplicates
						toDelete.append(i - 1)
						pronunciation[i] = pronunciation[i - 1]
					if(letter in ['y', 'w'] and prevLetter == letter):#delete duplicate
						pronunciation[i - 1] += pronunciation[i - 1]
						toDelete.append(i);
					
					prevLetter = letter
				for i in reversed(range(0, len(toDelete))):
					del(pronunciation[toDelete[i]])
				result += word[2:-2] + ' ' + ' '.join(pronunciation) + '\n'
			
			#Append utterance pronunciation to utterancesPronunciations
			utterancesPronuncations[-1] += " " + " ".join(pronunciations[0])
		else:
			utterancesPronuncations[-1] += " sil"
	
	#Add sound file name back
	utterancesPronuncations[-1] = wavFileName + ' "' + utterancesPronuncations[-1].strip() + '"'

#----------------------------------------------------------------------------
#Save output-----------------------------------------------------------------
#----------------------------------------------------------------------------
#Save Utterances pronunciations
outFile = codecs.open('utterance-pronunciations.txt', 'w', u'utf-8')
outFile.write("\n".join(utterancesPronuncations))
outFile.close()

#Save Pronunciation Dictionary
outFile = codecs.open('dict', 'w', u'utf-8')
outFile.write(result.rstrip())
outFile.close()

#Sort Dictionary
os.system("sortandfilter.py dict")