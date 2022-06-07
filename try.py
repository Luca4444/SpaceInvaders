import pickle

# objects = []
# with (open("best1654637245.pickle", "rb")) as openfile:
#     while True:
#         try:
#             objects.append(pickle.load(openfile))
#         except EOFError:
#             break
#
#
# print(objects)


hola= [3,3,3]
f = "pickles/best-t.pickle"
pickle.dump(hola, open(f, "wb"))