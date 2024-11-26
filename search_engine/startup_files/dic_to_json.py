import pickle, re, json

def main():
	found = {}
	s = None

	with open("synonym.dat","rb") as f:
		s = pickle.load(f)

	for i in s:
		if s[i][0] not in found: found[s[i][0]] = [i]
		else: found[s[i][0]].append(i)

	temp = found.copy()
	for j in temp:
		if len(temp[j]) == 1: found.pop(j)

	print(len(found))

	for k in found:
		count = 0
		print(k)
		for titles in found[k]:
			print(f"\t{titles} ({count})")
			count += 1
		while (True):
			x = input("Choose: ")
			if x == "none":
				for titles in found[k]: s.pop(titles)
				break
			elif x == "all":
				break
			else:
				try:
					x = int(x)
					found[k].pop(x)
					for titles in found[k]: s.pop(titles)
					break
				except:
					print("try again")

	with open("synonym2.dat", "wb") as f:
		pickle.dump(s, f)


if __name__ == '__main__':
	main()