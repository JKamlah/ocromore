from n_dist_keying.distance_storage import DistanceStorage
from n_dist_keying.text_comparator import TextComparator
from n_dist_keying.text_unspacer import TextUnspacer
import numpy as np
from multi_sequence_alignment.msa_handler import MsaHandler
from utils.random import Random


import inspect


class OCRset:
    """
        A storage class for a y_mean value
        and a set of lines which was assigned to each other
        If the lineset values where not edited, they are intialized with 'False
    """
    N_DISTANCE_SHORTEST_TAG = "n_distance_shortest"

    def __init__(self, lines_size, y_mean):
        lineset = []
        for x in range(0, lines_size):
            lineset.append(False)

        self._set_lines = lineset
        self._size = lines_size
        self._y_mean = y_mean  # mean y coordinate of all lines referenced in this set
        self.d_storage = DistanceStorage()
        self.shortest_distance_line_index = -1
        self._unspaced = False  # indicates the set_lines was unspaced
        self._refspaced = False # indicates the set_lines was reference spaced
        self._text_unspacer = TextUnspacer()
        self.shortest_distance_line = None  # holder element for recognized shortest distance line
        self._best_msa_text =""
        self._is_origin_database = False
        self._database_handler = None

    def is_database_set(self, enabled, database_handler):
        self._is_origin_database = enabled
        self._database_handler = database_handler

    def edit_line_set_value(self, set_index, new_value):
        self._set_lines[set_index] = new_value

    def get_line_set_value_line(self, set_index):
        return self._set_lines[set_index]

    def get_line_set_value_text(self, set_index):
        value_line = self.get_line_set_value_line(set_index)
        value_text = self.get_line_content(value_line)
        return value_text

    def get_msa_best_text(self):
        return self._best_msa_text

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size= value

    @property
    def y_mean(self):
        return self._y_mean

    @y_mean.setter
    def y_mean(self, value):
        self.y_mean = value

    def calculate_y_mean(self):
        """
        Goes through set elements and calculates y_mean for y_start and y_stop values
        :return:
        """

        acc_counter = 0
        y_start_final = 0
        y_stop_final = 0

        for line in self._set_lines:
            # don't count undefined values for means
            if line is False or line is None:
                continue
            # accumulate y-values
            (x_start, y_start, x_stop, y_stop) = line.coordinates
            y_start_final = y_start_final + y_start
            y_stop_final = y_stop_final + y_stop
            # add number of accumulation count
            acc_counter = acc_counter +1

        y_start_mean = y_start_final/acc_counter
        y_stop_mean = y_stop_final/acc_counter
        y_mean = (y_start_mean + y_stop_mean) / 2

        self._y_mean = round(y_mean)



    def is_full(self):
        """
        Checks if all lines are defined in the lineset
        :return: True or False
        """
        for line in self._set_lines:
            if line is False:
                return False

        return True

    def print_me(self, diff_only=False):

        lineset_acc=""
        one_line_is_false = False

        for line in self._set_lines:
            try:
                ocr_text = self.get_line_content(line)
                if ocr_text is False:
                    one_line_is_false = True
                    lineset_acc = lineset_acc+str(ocr_text)+"||"
                else:
                    lineset_acc = lineset_acc+ocr_text+"||"

            except:
                print("problem creating printable lineset ")

        lineset_acc = lineset_acc + "||"
        msa_str = str(self._best_msa_text)
        if diff_only is True:
            if one_line_is_false is True:
                print(str(self.y_mean) + "||"+msa_str+"||"+str(self.shortest_distance_line_index)+"||" + lineset_acc)
        else:
            print(str(self.y_mean)+"||"+msa_str+"||"+str(self.shortest_distance_line_index)+"||"+lineset_acc)



    def calculate_n_distance_keying(self):

        #if self.y_mean == 2123:
        #    print("Stop here")

        # do a line-wise comparison, which calculates a distance between all lines in this set
        for line_index, line in enumerate(self._set_lines):
            self.compare_with_other_lines(line_index, line)

        # calculate the distance from each item in set to all others
        for line_index, line in enumerate(self._set_lines):
            self.d_storage.calculate_accumulated_distance(line_index)

        # get the index of the item in set, which has the shortest distance to all others
        self.d_storage.calculate_shortest_distance_index()

        # save the result
        shortest_dist_index = self.d_storage.get_shortest_distance_index()
        self.shortest_distance_line_index = shortest_dist_index
        self.shortest_distance_line = self._set_lines[shortest_dist_index]

    def calculate_n_distance_keying_wordwise(self):
        if self._is_origin_database is False:
            raise Exception("Wordwise keying only possible with database originated ocr_sets")

        # get maximum word index
        max_word_indices = []
        for line in self._set_lines:
            if line is False or line is None:
                max_word_indices.append(0)
            else:
                max_word_index = int(max(line.data["word_idx"]))
                max_word_indices.append(max_word_index)

        max_word_index = max(max_word_indices)
        print("mwi",max_word_index)

        def get_word_at_calc_wordindex(line, word_index):
            accumulated_word = ""
            word_indices = line.data["calc_word_idx"]

            for char_index, char in enumerate(line.data["char"]):
                current_word_index = word_indices[char_index]
                if current_word_index == word_index:
                    accumulated_word +=char
                if current_word_index > word_index:
                    break
            return accumulated_word

        # get corresponding words
        for current_word_index in range(0,max_word_index):
            words = []
            for line in self._set_lines:
                if line is False or line is None:
                    words.append(False)
                else:
                    if current_word_index < int(max(line.data["calc_word_idx"])):
                        current_word = get_word_at_calc_wordindex(line, current_word_index)
                        words.append(current_word)
                    else:
                        words.append(False)

            print(words)
            print("--")

        return
        #if self.y_mean == 2123:
        #    print("Stop here")

        # do a line-wise comparison, which calculates a distance between all lines in this set
        for line_index, line in enumerate(self._set_lines):
            self.compare_with_other_lines(line_index, line)

        # calculate the distance from each item in set to all others
        for line_index, line in enumerate(self._set_lines):
            self.d_storage.calculate_accumulated_distance(line_index)

        # get the index of the item in set, which has the shortest distance to all others
        self.d_storage.calculate_shortest_distance_index()

        # save the result
        shortest_dist_index = self.d_storage.get_shortest_distance_index()
        self.shortest_distance_line_index = shortest_dist_index
        self.shortest_distance_line = self._set_lines[shortest_dist_index]


    def get_longest_index(self):

        def if_notdef_set_emptystring(value):
            if value is True or value is False or value is None:
                return ""

            return value

        lsval_1 = if_notdef_set_emptystring(self.get_line_content(self.get_line_set_value_line(0)))
        lsval_2 = if_notdef_set_emptystring(self.get_line_content(self.get_line_set_value_line(1)))
        lsval_3 = if_notdef_set_emptystring(self.get_line_content(self.get_line_set_value_line(2)))

        len_pline_1 = len(lsval_1)
        len_pline_2 = len(lsval_2)
        len_pline_3 = len(lsval_3)
        # max_index_value = max([len_pline_1, len_pline_2, len_pline_3])
        max_index = np.argmax([len_pline_1, len_pline_2, len_pline_3])
        print(max_index)
        return max_index

    def calculate_msa_best(self, take_n_dist_best_index=False, take_longest_as_pivot = False):


        # do a preselection of best element, if the parameter is set to take best n_dist_index as a pivot
        best_index = 1
        if take_longest_as_pivot is True:
            best_index = self.get_longest_index()
        elif take_n_dist_best_index is True:
            best_index = self.get_shortest_n_distance_index()


        indices = [0, 1, 2]
        indices.remove(best_index)
        index1 = indices[0]
        index2 = indices[1]

        print("msa selection taking best:",best_index, "others:(", index1, "and", index2,")")

        try:
            line_1 = self.get_line_content(self._set_lines[index1])
            line_2 = self.get_line_content(self._set_lines[best_index]) # should be best
            line_3 = self.get_line_content(self._set_lines[index2])

            print("ocr_set:")
            print("text_A",line_1)
            print("text_B",line_2)
            print("text_C",line_3)


            lines = [line_1, line_2, line_3]

            line_1_ok = not Random.is_false_true_or_none(line_1)
            line_2_ok = not Random.is_false_true_or_none(line_2)
            line_3_ok = not Random.is_false_true_or_none(line_3)
            ok_lines = [line_1_ok, line_2_ok, line_3_ok]
            not_ok_indices = []
            ok_indices = []
            for ok_index, ok in enumerate(ok_lines):
                if ok is True:
                    # not_ok_indices.append(ok_index)
                    ok_indices.append(ok_index)

            ok_len = len(ok_indices)

            if ok_len ==1:
                result = lines[ok_indices[0]]
            elif ok_len == 0:
                result = None
            elif ok_len == 2:
                result = lines[ok_indices[0]]
            else:
                result = MsaHandler.get_best_of_three(line_1, line_2, line_3)

            self._best_msa_text = result
        except Exception as e:
            print("Exception in MSA, just taking line prio exception:", e)
            tr = inspect.trace()

            self._best_msa_text = self.get_line_content(self._set_lines[1])



    def calculate_msa_best_charconf(self, take_n_dist_best_index=False, take_longest_as_pivot = True):

        # do a preselection of best element, if the parameter is set to take best n_dist_index as a pivot
        best_index = 1

        if take_n_dist_best_index is True:
            ldist_best_index = self.get_shortest_n_distance_index() # this doesn't work in all cases atm
            best_index = ldist_best_index
        if take_longest_as_pivot is True:
            best_index = self.get_longest_index()

        indices = [0, 1, 2]
        indices.remove(best_index)
        index1 = indices[0]
        index2 = indices[1]

        print("msa selection taking best:",best_index, "others:(", index1, "and", index2,")")

        try:

            line_1 = self._set_lines[index1]
            line_2 = self._set_lines[best_index]
            line_3 = self._set_lines[index2]

            text_1 = self.get_line_content(line_1)
            text_2 = self.get_line_content(line_2) # should be best
            text_3 = self.get_line_content(line_3)

            print("ocr_set:")
            print("text_A", text_1)
            print("text_B", text_2)
            print("text_C", text_3)


            lines = [text_1, text_2, text_3]

            line_1_ok = not Random.is_false_true_or_none(text_1)
            line_2_ok = not Random.is_false_true_or_none(text_2)
            line_3_ok = not Random.is_false_true_or_none(text_3)
            ok_lines = [line_1_ok, line_2_ok, line_3_ok]
            not_ok_indices = []
            ok_indices = []
            for ok_index, ok in enumerate(ok_lines):
                if ok is True:
                    # not_ok_indices.append(ok_index)
                    ok_indices.append(ok_index)

            ok_len = len(ok_indices)

            if ok_len == 0:
                result = None
            else:
                result = MsaHandler.get_best_of_three(text_1, text_2, text_3, use_charconfs=True, \
                                                      line_1=line_1,line_2=line_2,line_3=line_3)

            self._best_msa_text = result
        except Exception as e:
            print("Exception in MSA, just taking line prio exception:", e)
            tr = inspect.trace()
            if take_n_dist_best_index is True:
                self._best_msa_text = self.get_line_content(self._set_lines[ldist_best_index])
            else:
                self._best_msa_text = self.get_line_content(self._set_lines[best_index])




    def get_shortest_n_distance_text(self):
        if self.shortest_distance_line_index >= 0:
            line = self.shortest_distance_line
            line_text = self.get_line_content(line)
            return line_text
        else:
            return None

    def set_shortest_n_distance_text(self, value):
        if self.shortest_distance_line_index >= 0:
            sd_line = self.shortest_distance_line
            sd_line_new_value = self.set_line_content(sd_line, value)
            self.set_shortest_n_distance_line(sd_line_new_value)
        else:
            return None


    def get_shortest_n_distance_line(self):
        if self.shortest_distance_line_index >= 0:
            line = self.shortest_distance_line
            return line
        else:
            return None

    def set_shortest_n_distance_line(self, value):
        self.shortest_distance_line = value


    def get_shortest_n_distance_index(self):
        if self.shortest_distance_line_index >= 0:
            return self.shortest_distance_line_index
        else:
            return None

    def print_shortest_n_distance_line(self):
        line = self.get_shortest_n_distance_text()
        if line is not None and line is not False:
            print(line)

    def print_msa_best_line(self):
        msa_text = self._best_msa_text
        if msa_text is not None and msa_text is not False:
            print(msa_text)
        else:
            print(str(msa_text))


    def compare_with_other_lines(self, line_index, line):
        ocr_text = self.get_line_content(line)

        for line_index_cmp, line_cmp in enumerate(self._set_lines):

            # if line has the same index, continue
            if line_index is line_index_cmp:
                continue

            existing_distance = self.d_storage.fetch_value(line_index, line_index_cmp)

            # if line was already compared, continue
            if existing_distance is not None:
                continue

            ocr_text_cmp = self.get_line_content(line_cmp)
            distance = self.get_distance(ocr_text, ocr_text_cmp)
            self.d_storage.store_value(line_index, line_index_cmp, distance)

    def get_distance(self, text1, text2):
        # todo add more possibilities for distance measurement, i.e confidences, edit distance, context weighting
        MODE_DIFFLIB = 'difflib' #best bet
        MODE_NORMED_LEVENSHTEIN = 'normed_levenshtein' # longest alignment normed levenshtein distance
        MODE_SORENSEN = 'sorensen'
        MODE_JACCARD = 'jaccard'
        MODE_HAMMING = 'hamming'
        MODE_MYERS = 'myers' # use myers special difflib sequence matcher
        mode = MODE_DIFFLIB # set your mode here

        # return a fixed negative value if one of the strings is not defined
        if text1 is False and text2 is False:
            return 0

        # One is false and one is not false
        if text1 is False or text2 is False:
            return 1

        dist = 1

        if mode == MODE_DIFFLIB:
            dist = TextComparator.compare_ocr_strings_difflib_seqmatch(text1, text2)

        elif mode == MODE_NORMED_LEVENSHTEIN:
            dist = TextComparator.compare_ocr_strings_levensthein_normed(text1, text2)

        elif mode == MODE_HAMMING:
            dist = TextComparator.compare_ocr_strings_hamming(text1, text2)

        elif mode == MODE_SORENSEN:
            dist = TextComparator.compare_ocr_strings_sorensen(text1, text2)

        elif mode == MODE_JACCARD:
            dist = TextComparator.compare_ocr_strings_jaccard(text1, text2)
        elif mode == MODE_MYERS:
            dist = TextComparator.compare_ocr_strings_myers(text1, text2)

        return dist

    def get_line_content(self, line):
        """
        Helper method to get line content, because ocropus content
        has other access properties. Method behaves differently when
        the current set is a database set
        :param line: line element to check upn
        :return: string with line content, or 'False if line isn't defined.
        """


        # hint: the attribute checked is created by hocr_line_normalizer
        if line is False:
            return False
        # elif hasattr(line, 'ocr_text_normalized'):

        if self._is_origin_database is False:
            # just the standard behaviour
            if line.ocr_text_normalized is not None:
                return line.ocr_text_normalized
            else:
                return line.ocr_text
        else:
            return line.textstr


    def set_line_content(self, line, value):
        """
        Helper method to set line content, because ocropus content
        has other access properties.
        :param line: line element to set the value to
        :param value: value to set to 'ocr_text_normalized' property
        :return: line or false if line not defined
        """

        # hint: the attribute checked is created by hocr_line_normalizer
        if line is False:
            return False

        line.ocr_text_normalized = value
        return line


    def unspace_lines(self, list_index_to_unspace, unspaced_list_index):

        unspaced_lines = self._text_unspacer.unspace_texts(self._set_lines, list_index_to_unspace, unspaced_list_index)

        self._unspaced = True
        self._refspaced = False
        self._set_lines = unspaced_lines


    def refspace_lines(self, list_index_to_adapt, list_index_reference):

        refspaced_lines = self._text_unspacer.refspace_texts(self._set_lines, list_index_to_adapt, list_index_reference)

        self._unspaced = False
        self._refspaced = True
        self._set_lines = refspaced_lines