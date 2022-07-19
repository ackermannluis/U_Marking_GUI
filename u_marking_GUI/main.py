#!/usr/bin/env python
# Copyright 2021
# author: Luis Ackermann <ackermann.luis@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from tkinter import *
from tkinter import messagebox, filedialog, simpledialog
import tkinter
import numpy as np
import os
import time
import xlsxwriter

"""
Change log:
- changed the format of the rubric input file
- added a way to add feedback into the rubric file, this will be the default way of creating the marking rubric
    allowing for starting marking from the rubric, without feedbacks, with the feedback options increasing as they are
    used.
- added a way to delete a feedback option.
- added scroll bar to feedback to account for many options
- added history option, allowing to revert back to previous marking state (kind of an undo)
- added marking report in excel format
- added error handling
- allowed the student list to be a csv (comma delimited)
"""

##########################################################################
#define needed classes
class VerticalScrolledFrame(Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling

    """
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0,bg='black',
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=1)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas,bg='black')
        interior_id = canvas.create_window(0, 0, window=interior, anchor=NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id)
        canvas.bind('<Configure>', _configure_canvas)
#initializing GUI
#Make object for application
def Main_Window(root):
    global Main_frame,frame_students,frame_questions,frame_main_2,frame_main_2_1,frame_feedback_selector
    global frame_feedback_display, frame_criteria, frame_student_details, frame_custom_feedback_display
    global menu_bar, load_menu, save_menu, about_menu, history_menu

    # <editor-fold desc="Frames">
    # Frames
    Main_frame = Frame(root, width=1000, height=100)
    Main_frame.configure(background='black')
    Main_frame.pack(fill=BOTH, expand=1)

    frame_students_wrapper =  VerticalScrolledFrame(Main_frame)
    frame_students_wrapper.pack(side=LEFT,fill=Y)
    frame_students = Frame(frame_students_wrapper.interior, bg='black')
    frame_students.pack(side=LEFT,fill=Y)

    frame_questions_wrapper =  VerticalScrolledFrame(Main_frame)
    frame_questions_wrapper.pack(side=LEFT,fill=Y)
    frame_questions = Frame(frame_questions_wrapper.interior)
    frame_questions.pack(side=LEFT,fill=Y)

    frame_main_2 = Frame(Main_frame,bg = 'black')
    frame_main_2.pack(side=LEFT,fill=BOTH, expand=1)

    frame_main_2_1 = Frame(frame_main_2,bg = 'black')
    frame_main_2_1.pack(side=TOP)#,fill=BOTH, expand=1)

    frame_feedback_selector_wrapper = VerticalScrolledFrame(frame_main_2,bg = 'black')
    frame_feedback_selector_wrapper.pack(side=TOP,fill=BOTH, expand=1)

    frame_feedback_selector = Frame(frame_feedback_selector_wrapper.interior,bg = 'black')
    frame_feedback_selector.pack(side=TOP,fill=BOTH, expand=1)

    frame_feedback_display = Frame(frame_main_2,bg = 'black')
    frame_feedback_display.pack(side=TOP)#,fill=BOTH, expand=1)

    frame_custom_feedback_display = Frame(frame_main_2,bg = 'black')
    frame_custom_feedback_display.pack(side=TOP)#,fill=BOTH, expand=1)

    frame_criteria = Frame(frame_main_2_1,bg = 'black')
    frame_criteria.pack(side=LEFT)#,fill=Y)

    frame_student_details = Frame(frame_main_2_1,bg = 'grey')
    frame_student_details.pack(side=RIGHT)#,fill=BOTH)

    # </editor-fold>


    # create a toplevel menu
    menu_bar = Menu(root)
    # <editor-fold desc="Data Load menu">
    # create a pulldown menu, Data Load
    load_menu = Menu(menu_bar, tearoff=0)
    load_menu.add_command(label= 'Start new marking', command = start_new_marking)
    load_menu.add_separator()
    load_menu.add_command(label= 'Load previous marking', command = create_students_and_rubric_from_previous_marking)
    #
    menu_bar.add_cascade(label="Load Data", menu=load_menu)
    menu_bar.add_separator()
    # </editor-fold>
    # <editor-fold desc="Data Save menu">
    # create a pulldown menu, Data Save
    save_menu = Menu(menu_bar, tearoff=0)
    save_menu.add_command(label="Save current marking progress", command=save_current_markings)
    save_menu.add_separator()
    save_menu.add_command(label="Save current rubric", command=save_rubric_dict)
    save_menu.add_separator()
    save_menu.add_command(label="Create marking report (excel format)", command=create_markings_report_excel)
    save_menu.add_command(label="Create marking report (text format)", command=create_markings_report)
    #
    menu_bar.add_cascade(label="Save Data", menu=save_menu)
    menu_bar.add_separator()
    # </editor-fold>

    # <editor-fold desc="Marking History">
    # create a pulldown menu, Data Save
    history_menu = Menu(menu_bar, tearoff=0)
    history_menu.add_command(label="Load previous marking state", command=revert_to_previous_marking_state)
    #
    menu_bar.add_cascade(label="Marking History", menu=history_menu)
    menu_bar.add_separator()
    # </editor-fold>

    # <editor-fold desc="About menu">
    # create a pulldown menu, About
    about_menu = Menu(menu_bar, tearoff=0)
    about_menu.add_command(label="U-Mark (Universal Marking)")
    about_menu.add_command(label="Version " + program_version)
    about_menu.add_command(label="Created by Luis Ackermann")
    about_menu.add_command(label="contact me at")
    about_menu.add_command(label="ackermann.luis@gmail.com")
    menu_bar.add_cascade(label="About", menu = about_menu)
    # </editor-fold>
    # display the menu
    root.config(menu=menu_bar)

    disable_save()



#___________________________________________________________________________________________________
# background functions
def error_handler(error_msg):
    tkinter.messagebox.showerror('Error', error_msg)
    # except BaseException as error_msg:
    #     error_handler('Error while defining the parameters \n ' + str(error_msg))
def select_filename(path_, title=None):
    file_name = filedialog.askopenfilename(defaultextension = '.npz', initialdir = path_,title=title)
    return file_name
def select_folder(path_):
    folder_str = filedialog.askdirectory(initialdir = path_)
    return folder_str
def save_dict(dict_, filename_):
    np.save(filename_, dict_)
def disable_load():
    menu_bar.entryconfig("Load Data", state="disabled")
def enable_save():
    menu_bar.entryconfig("Save Data", state="normal")
def disable_save():
    menu_bar.entryconfig("Save Data", state="disabled")
def clearFrame(frame):
    # destroy all widgets from frame
    for widget in frame.winfo_children():
        widget.destroy()

    # this will clear frame and frame will be empty
    # # if you want to hide the empty panel then
    # frame.pack_forget()

#___________________________________________________________________________________________________
# load data
def load_student_dict():
    global filename_students, student_dict
    filename_students = select_filename(path_program, title='Select file with student list')

    file_ = open(filename_students, 'r')
    file_lines = file_.readlines()
    file_.close()

    if filename_students.split('.')[-1] == 'txt':
        delimiter_ = '|'
    else:
        delimiter_ = ','
    student_dict = {}
    for line_text in file_lines[1:]:
        student_id,student_name,student_surname,student_email = line_text.split(delimiter_)
        student_dict[student_id] = student_name + '\n' + student_surname + '\n' + student_email

    return student_dict
def load_rubric_dict():
    global filename_rubric, rubric_dict
    filename_rubric = select_filename(path_program, title='Select file with rubric structure and information')

    if filename_rubric[-3:] == 'npy':
        return np.load(filename_rubric, allow_pickle=True).item()
    else:
        file_ = open(filename_rubric, 'r')
        file_lines = file_.readlines()
        file_.close()

        rubric_dict = {}
        question_number = 1
        r_ = -1
        while r_ < len(file_lines)-1:
            r_ += 1
            if '#!Question name:' in file_lines[r_]:
                question_text = file_lines[r_][len('#!Question name:'):].strip()
                r_ += 1
                question_total_mark = float(file_lines[r_][len('#!Question marks:'):].strip())
                r_ += 1
                question_grading_divisions = int(file_lines[r_][len('#!Marking resolution:'):].strip())
                r_ += 1
                weights_list=[]
                marking_sub_criterias_list=[]
                while not '#!Standard Feedback options:' in file_lines[r_+1]:
                    r_ += 1
                    weight, criteria_ = file_lines[r_].strip().split('|')
                    weights_list.append(float(weight))
                    marking_sub_criterias_list.append(criteria_)
                marking_sub_criterias_weights_array = np.array(weights_list, dtype=float)
                marking_sub_criterias_weights_array_norm = (marking_sub_criterias_weights_array /
                                                            marking_sub_criterias_weights_array.sum())
                r_ += 1
                question_feedbacks_list=[]
                while not '-------------------' in file_lines[r_+1]:
                    r_ += 1
                    question_feedbacks_list.append(file_lines[r_].strip())
                r_ += 1

                # create weighted arrays
                mark_ratios = np.zeros(question_grading_divisions, dtype=float)
                for column_ in range(question_grading_divisions):
                    mark_ratios[column_] = column_ * (1 / (question_grading_divisions - 1))

                question_marks_weighted_array = np.zeros((len(marking_sub_criterias_list),
                                                          question_grading_divisions), dtype=float)
                for row_ in range(len(marking_sub_criterias_list)):
                    for column_ in range(question_grading_divisions):
                        question_marks_weighted_array[row_, column_] = question_total_mark * \
                                                                marking_sub_criterias_weights_array_norm[row_] * \
                                                                mark_ratios[column_]

                # store to output dict
                rubric_dict[str(question_number)] = {
                    'question_total_mark':question_total_mark,
                    'question_text': question_text,
                    'marking_sub_criterias_list': marking_sub_criterias_list,
                    'marking_sub_criterias_weights_array_norm': marking_sub_criterias_weights_array_norm,
                    'question_grading_divisions': question_grading_divisions,
                    'question_feedbacks_list': question_feedbacks_list,
                    'question_marks_weighted_array': question_marks_weighted_array,
                }
                question_number += 1

        return rubric_dict

def create_students_and_rubric_from_previous_marking():
    global filename_rubric, rubric_dict, filename_students, student_dict, \
        previous_marking_filename, marks_dict, selected_student_id, selected_question, history_dict

    try:
        previous_marking_filename = select_filename(path_program, title='Select file with previous markings (.npy)')
        previous_marking_dict = np.load(previous_marking_filename, allow_pickle=True).item()

        rubric_dict = previous_marking_dict['rubric_dict']
        student_dict = previous_marking_dict['student_dict']
        marks_dict = previous_marking_dict['marks_dict']
        filename_rubric = previous_marking_dict['filename_rubric']
        filename_students = previous_marking_dict['filename_students']
        selected_student_id = previous_marking_dict['selected_student_id']
        selected_question = previous_marking_dict['selected_question']
        history_dict = previous_marking_dict['history_dict']

        disable_load()
        enable_save()

        root.title(root_title + '--' + filename_rubric + '--' + filename_students + '--' + previous_marking_filename)


        create_student_buttons()
        create_question_buttons()

        history_dict_keys = sorted(history_dict.keys())
        create_students_and_rubric_from_history(history_dict[history_dict_keys[-1]])
    except BaseException as error_msg:
        error_handler('Error\n' + str(error_msg))
def create_students_and_rubric_from_history(history_dict_selected):
    global filename_rubric, rubric_dict, filename_students, student_dict, \
        previous_marking_filename, marks_dict, selected_student_id, selected_question



    rubric_dict = history_dict_selected['rubric_dict']
    student_dict = history_dict_selected['student_dict']
    marks_dict = history_dict_selected['marks_dict']
    filename_rubric = history_dict_selected['filename_rubric']
    filename_students = history_dict_selected['filename_students']
    selected_student_id = history_dict_selected['selected_student_id']
    selected_question = history_dict_selected['selected_question']

    disable_load()
    enable_save()

    mask_students(student_id_list.index(selected_student_id))
    mask_questions(questions_list.index(selected_question))
def create_marks_dict(student_dict, rubric_dict):
    global marks_dict

    marks_dict = {}
    questions_list = sorted(rubric_dict.keys())
    student_id_list = sorted(student_dict.keys())
    for student_id in student_id_list:
        marks_dict[student_id] = {}
        marks_dict[student_id]['total_grade'] = 'not marked'
        for question_number in questions_list:
            marks_dict[student_id][question_number] = {}
            number_of_subcriteria = len(rubric_dict[question_number]['marking_sub_criterias_list'])
            number_of_mark_options = rubric_dict[question_number]['question_grading_divisions']
            number_of_feedbacks = len(rubric_dict[question_number]['question_feedbacks_list'])
            marks_dict[student_id][question_number]['sub_criteria_mark_mask_array'] = \
                np.zeros((number_of_subcriteria,number_of_mark_options),dtype=float)
            marks_dict[student_id][question_number]['sub_criteria_mark_mask_array'][:,0] = 1
            marks_dict[student_id][question_number]['sub_criteria_feedback_mask_array'] = \
                np.zeros(number_of_feedbacks,dtype=bool)
            marks_dict[student_id][question_number]['custom_feedback'] = ''
            marks_dict[student_id][question_number]['feedback'] = ''

def revert_to_previous_marking_state():
    global history_dict
    prompt_ = 'Input number of previous state to load:'

    history_dict_states = sorted(history_dict.keys())


    for i_, history_key in enumerate(history_dict_states):
        prompt_ += '\n' + str(1+i_).zfill(2) + '  =  ' + history_key + \
                   ' -- grading student ' + history_dict[history_key]['selected_student_id'] + \
                   ' on question ' + history_dict[history_key]['selected_question']

    history_key_index = simpledialog.askinteger('Input',prompt_)

    if history_key_index is not None and 0 < history_key_index < len(history_dict_states)+1:
        selected_history_key = history_dict_states[history_key_index-1]

        create_students_and_rubric_from_history(history_dict[selected_history_key])
def start_new_marking():
    global history_dict
    try:
        load_rubric_dict()
        load_student_dict()
        create_marks_dict(student_dict, rubric_dict)
        history_dict = {}

        disable_load()
        enable_save()

        root.title(root_title + '--' + filename_rubric + '--' + filename_students)

        create_student_buttons()
        create_question_buttons()

        mask_students(0)
        mask_questions(0)
    except BaseException as error_msg:
        error_handler('Error\n' + str(error_msg))

# save data
def save_rubric_dict():
    try:
        filename_rubric = filedialog.asksaveasfilename(initialdir=path_program,
                                                       confirmoverwrite=True,
                                                       title='Select output filename for current rubric')
        save_dict(rubric_dict, filename_rubric)
    except BaseException as error_msg:
        error_handler('Error\n' + str(error_msg))
def save_current_markings():
    try:
        previous_marking_filename = filedialog.asksaveasfilename(initialdir=path_program,
                                                                 confirmoverwrite=True,
                                                                 title='Select output filename for current markings')

        previous_marking_dict = {
            'rubric_dict':rubric_dict,
            'student_dict': student_dict,
            'marks_dict': marks_dict,
            'filename_rubric': filename_rubric,
            'filename_students': filename_students,
            'selected_student_id':selected_student_id,
            'selected_question': selected_question,
            'history_dict': history_dict,
        }
        save_dict(previous_marking_dict, previous_marking_filename)
    except BaseException as error_msg:
        error_handler('Error\n' + str(error_msg))
def create_markings_report():
    try:
        marking_report_filename = filedialog.asksaveasfilename(initialdir=path_program,
                                                               confirmoverwrite=True,
                                                               title='Select output filename for markings report')
        if marking_report_filename != '':
            file_report = open(marking_report_filename, 'w')

            student_id_list = sorted(student_dict.keys())

            for student_id in student_id_list:
                file_report.write('-'*40            +'\n')
                file_report.write('student_id: ' + student_id        +'\n')
                file_report.write(student_dict[student_id]        +'\n')
                file_report.write('Total Grade: ' + marks_dict[student_id]['total_grade']         +'\n')
                for question_number in sorted(rubric_dict.keys()):
                    feedback_text = marks_dict[student_id][question_number]['feedback']
                    file_report.write('\n')
                    feedback_text += marks_dict[student_id][question_number]['custom_feedback']
                    file_report.write(feedback_text + '\n')

            file_report.close()
    except BaseException as error_msg:
        error_handler('Error\n' + str(error_msg))
def create_markings_report_excel():
    try:
        marking_report_filename = filedialog.asksaveasfilename(initialdir=path_program,
                                                               confirmoverwrite=True,
                                                               title='Select output filename for markings report')
        if marking_report_filename != '':

            if marking_report_filename[-5:] != '.xlsx':
                marking_report_filename = marking_report_filename + '.xlsx'

            workbook = xlsxwriter.Workbook(marking_report_filename)
            bold = workbook.add_format({'bold': True})

            worksheet = workbook.add_worksheet()
            worksheet.set_column(0,0,15)
            worksheet.set_column(1,1,25)
            worksheet.set_column(2,2,22)
            worksheet.set_column(3,3,30)

            current_time_struct = time.gmtime()
            current_time_str = str(current_time_struct[0]).zfill(4) + '-' + \
                               str(current_time_struct[1]).zfill(2) + '-' + \
                               str(current_time_struct[2]).zfill(2) + ' ' + \
                               str(current_time_struct[3]).zfill(2) + ':' + \
                               str(current_time_struct[4]).zfill(2) + ':' + \
                               str(current_time_struct[5]).zfill(2)
            worksheet.write('A1', 'Marking Report', bold)
            worksheet.write('B1', current_time_str, bold)

            # write header
            worksheet.write('A2', 'Student ID', bold)
            worksheet.write('B2', 'Student Name', bold)
            worksheet.write('C2', 'Student Surname', bold)
            worksheet.write('D2', 'Student email', bold)

            worksheet.write('N1', 'Feedback', bold)


            student_id_list = sorted(student_dict.keys())

            # write question names and marks
            question_number_list = sorted(rubric_dict.keys())
            assigment_total = 0
            for i_, question_number in enumerate(question_number_list):
                worksheet.write(0, i_ + 4, rubric_dict[question_number]['question_text'], bold)
                worksheet.write(1, i_ + 4, rubric_dict[question_number]['question_total_mark'], bold)
                assigment_total += rubric_dict[question_number]['question_total_mark']
            worksheet.write(0, i_ + 4 + 1, 'TOTAL', bold)
            worksheet.write(1, i_ + 4 + 1, assigment_total, bold)


            # write marks
            for r_, student_id in enumerate(student_id_list):
                # write student details
                student_details_list = student_dict[student_id].split('\n')
                worksheet.write(r_ + 2, 0, student_id)
                worksheet.write(r_ + 2, 1, student_details_list[0])
                worksheet.write(r_ + 2, 2, student_details_list[1])
                worksheet.write(r_ + 2, 3, student_details_list[2])

                # write student marking
                total_student_mark = 0
                feedback_text = ''
                for c_, question_number in enumerate(question_number_list):

                    question_mark = (rubric_dict[question_number]['question_marks_weighted_array'] *
                                     marks_dict[student_id][question_number][ 'sub_criteria_mark_mask_array']).sum()
                    worksheet.write(r_ + 2, 4 + c_, np.round(question_mark,2))
                    total_student_mark += question_mark

                    feedback_text += marks_dict[student_id][question_number]['feedback'] + \
                                     marks_dict[student_id][question_number]['custom_feedback'] + '\n'

                worksheet.write(r_ + 2, 4 + c_ + 1, np.round(total_student_mark,2))

                # write student feedback
                worksheet.write(r_ + 2, 13, feedback_text)

            workbook.close()
    except BaseException as error_msg:
        error_handler('Error\n' + str(error_msg))

def save_history():
    global history_dict

    try:
        current_time_struct = time.gmtime()

        current_time_str = str(current_time_struct[0]).zfill(4) + '-' + \
                           str(current_time_struct[1]).zfill(2) + '-' + \
                           str(current_time_struct[2]).zfill(2) + ' ' + \
                           str(current_time_struct[3]).zfill(2) + ':' + \
                           str(current_time_struct[4]).zfill(2) + ':' + \
                           str(current_time_struct[5]).zfill(2)

        history_dict[current_time_str] = {
            'rubric_dict':rubric_dict,
            'student_dict': student_dict,
            'marks_dict': marks_dict,
            'filename_rubric': filename_rubric,
            'filename_students': filename_students,
            'selected_student_id':selected_student_id,
            'selected_question': selected_question,
        }

        history_dict_keys = sorted(history_dict.keys())
        if len(history_dict_keys) > 20:
            del history_dict[history_dict_keys[0]]
    except BaseException as error_msg:
        error_handler('Error\n' + str(error_msg))

        # button functions
def create_student_buttons():
    global student_button_list, student_button_number_to_id_map, selected_student_id, student_id_list

    # add label to frame
    label_text = tkinter.Label(frame_students,
                                        text = "Students' IDs",
                                        bg='grey', fg='white', font=font_size)
    label_text.grid(row=0,column=0, columnspan=1)

    student_button_list = []

    student_id_list = sorted(student_dict.keys())
    selected_student_id = student_id_list[0]
    student_button_number_to_id_map = {}
    for i, student_id in enumerate(student_id_list):
        student_button_number_to_id_map[i] = student_id

        student_button_list.append(tkinter.Button(frame_students, text=student_id,
                                                  command=lambda arg_2=i: mask_students(arg_2),
                                                  bg='gray48', font=("Arial", student_id_font_size)))
        student_button_list[i].grid(row=1 + i, column=0, sticky='W,E')
    student_button_list[0].configure(bg='red')
def create_question_buttons():
    global question_button_list, question_button_number_to_number_map, selected_question, questions_list

    # add label to frame
    label_text = tkinter.Label(frame_questions,
                                        text = "Question #",
                                        bg='grey', fg='white', font=font_size)
    label_text.grid(row=0,column=0, columnspan=1)

    question_button_list = []

    questions_list = sorted(rubric_dict.keys())
    selected_question = questions_list[0]
    question_button_number_to_number_map = {}
    for i, question_number in enumerate(questions_list):
        question_button_number_to_number_map[i] = question_number


        question_button_list.append(tkinter.Button(frame_questions, text=question_number,
                                                   command=lambda arg_2=i: mask_questions(arg_2),
                                                   bg='gray48', font=("Arial", question_number_font_size)))
        question_button_list[i].grid(row=1 + i, column=0, sticky='W,E')

    question_button_list[0].configure(bg='red')
def mask_students(botton_index):
    global selected_student_id, student_button_list
    try:
        selected_student_id = student_button_number_to_id_map[botton_index]

        # change color on parameter button
        for student_button in student_button_list:
            student_button.configure(bg = 'gray48')
        student_button_list[botton_index].configure(bg = 'red')
        save_history()
        display_student_marking()
    except BaseException as error_msg:
        error_handler('Error\n' + str(error_msg))
def mask_questions(botton_index):
    global selected_question, question_button_list
    try:
        selected_question = question_button_number_to_number_map[botton_index]

        # change color on parameter button
        for student_button in question_button_list:
            student_button.configure(bg='gray48')
        question_button_list[botton_index].configure(bg='red')

        save_history()
        display_student_marking()
    except BaseException as error_msg:
        error_handler('Error\n' + str(error_msg))
def update_criteria(arg_):
    global marks_dict
    try:
        r_, c_ = arg_
        marks_dict[selected_student_id][selected_question]['sub_criteria_mark_mask_array'][r_, :] = 0
        marks_dict[selected_student_id][selected_question]['sub_criteria_mark_mask_array'][r_, c_] = 1

        display_student_marking()
    except BaseException as error_msg:
        error_handler('Error\n' + str(error_msg))
def update_feedback(feedback_index):
    global marks_dict
    try:
        if marks_dict[selected_student_id][selected_question]['sub_criteria_feedback_mask_array'][feedback_index]:
            marks_dict[selected_student_id][selected_question]['sub_criteria_feedback_mask_array'][feedback_index] = False
        else:
            marks_dict[selected_student_id][selected_question]['sub_criteria_feedback_mask_array'][feedback_index] = True

        display_student_marking()
    except BaseException as error_msg:
        error_handler('Error\n' + str(error_msg))
def save_custom_feedback():
    global marks_dict
    try:
        custom_feedback_text = custom_feedback_display.get('1.0', END)
        marks_dict[selected_student_id][selected_question]['custom_feedback'] = custom_feedback_text
    except BaseException as error_msg:
        error_handler('Error\n' + str(error_msg))
def add_feedback_option():
    global rubric_dict, marks_dict
    try:
        feedback_text = simpledialog.askstring('Input',
                                               'Input feedback text to be added to options for this question')

        if feedback_text != '' and feedback_text is not None:
            rubric_dict[selected_question]['question_feedbacks_list'].append(feedback_text)
            for student_id in student_id_list:
                feedback_mask = marks_dict[student_id][selected_question]['sub_criteria_feedback_mask_array']
                feedback_mask_new = np.zeros((len(rubric_dict[selected_question]['question_feedbacks_list'])), dtype=bool)
                feedback_mask_new[:-1] = feedback_mask
                marks_dict[student_id][selected_question]['sub_criteria_feedback_mask_array'] = feedback_mask_new

            display_student_marking()
    except BaseException as error_msg:
        error_handler('Error\n' + str(error_msg))
def delete_feedback_option():
    global rubric_dict, marks_dict
    try:
        prompt_ = 'Input number of feedback to be deleted from the following:'

        for i_, feedback_option in enumerate(rubric_dict[selected_question]['question_feedbacks_list']):
            prompt_ += '\n' + str(1+i_) + '  =  ' + feedback_option

        feedback_index = simpledialog.askinteger('Input',prompt_)
        print(feedback_index)

        if feedback_index is not None and\
                0 < feedback_index < len(rubric_dict[selected_question]['question_feedbacks_list'])+1:

            for student_id in student_id_list:
                # check if feedback is selected for this student
                if marks_dict[student_id][selected_question]['sub_criteria_feedback_mask_array'][feedback_index - 1]:
                    # add this feedback to custom before deleting it
                    marks_dict[student_id][selected_question]['custom_feedback'] += \
                        rubric_dict[selected_question]['question_feedbacks_list'][feedback_index - 1] + '\n'

                marks_dict[student_id][selected_question]['sub_criteria_feedback_mask_array'] = \
                    np.delete(marks_dict[student_id][selected_question]['sub_criteria_feedback_mask_array'],
                              (feedback_index - 1), axis=0)


            del rubric_dict[selected_question]['question_feedbacks_list'][feedback_index - 1]
            for student_id in student_id_list:
                # update standard feedback
                current_mark = (rubric_dict[selected_question]['question_marks_weighted_array'] *
                                marks_dict[student_id][selected_question][
                                    'sub_criteria_mark_mask_array']).sum()
                marks_dict[student_id][selected_question]['feedback'] = \
                    create_question_feedback_text(selected_question, student_id, current_mark)



            display_student_marking()
    except BaseException as error_msg:
        error_handler('Error\n' + str(error_msg))
def create_question_feedback_text(question_, student_, question_mark):
    # feedback display
    feedback_display_text = 'Question: ' + rubric_dict[question_]['question_text']
    feedback_display_text += " ({0:.2f}/{1:.2f})\n\n".format(question_mark,
                                                             rubric_dict[question_]['question_total_mark'])
    feedback_display_text += 'Specific feedback:\n'

    for i_, feedback_text in enumerate(rubric_dict[question_]['question_feedbacks_list']):
        if marks_dict[student_][question_]['sub_criteria_feedback_mask_array'][i_]:
            feedback_display_text += feedback_text + '\n'
    return feedback_display_text

def display_student_marking():
    global criteria_button_list, feedback_button_list, custom_feedback_display, custom_feedback_save_button

    try:

        # calculate current mark
        current_mark = (rubric_dict[selected_question]['question_marks_weighted_array'] *
                        marks_dict[selected_student_id][selected_question]['sub_criteria_mark_mask_array']).sum()


        # clear previous selections
        clearFrame(frame_student_details)
        clearFrame(frame_criteria)
        clearFrame(frame_feedback_selector)
        clearFrame(frame_feedback_display)
        clearFrame(frame_custom_feedback_display)

        # display question text
        text_ = rubric_dict[selected_question]['question_text'] + \
                ' (current marks={0:.2f}/{1:.2f})'.format(current_mark,
                                                          rubric_dict[selected_question]['question_total_mark'])
        label_text = tkinter.Label(frame_criteria,
                                   text = text_,
                                   bg='grey', fg='white', font=font_size)
        label_text.grid(row=0,column=0, columnspan=rubric_dict[selected_question]['question_grading_divisions']+1)

        # display criteria list
        for i_, criteria_text in enumerate(rubric_dict[selected_question]['marking_sub_criterias_list']):
            label_text = tkinter.Label(frame_criteria,
                                       text=criteria_text,
                                       bg='grey', fg='black', font=font_size)
            label_text.grid(row=i_+1, column=0, columnspan=1, sticky='E')


        # create_sub_criteria_buttons
        criteria_button_list=[]
        for r_ in range(len(rubric_dict[selected_question]['marking_sub_criterias_list'])):
            for c_ in range(rubric_dict[selected_question]['question_grading_divisions']):
                percentage_str = '{0:.0f}%'.format(c_ * (100/(rubric_dict[selected_question]['question_grading_divisions']-1)))
                criteria_button_list.append(tkinter.Button(frame_criteria, text=percentage_str,
                                                          command=lambda arg_2=(r_,c_): update_criteria(arg_2),
                                                          bg='gray48', font=font_size))
                criteria_button_list[-1].grid(row=1 + r_, column=1 + c_, sticky='W,E', columnspan=1)

                if marks_dict[selected_student_id][selected_question]['sub_criteria_mark_mask_array'][r_,c_] == 1:
                    criteria_button_list[-1].configure(bg='red')



        # display student details
        label_text = tkinter.Label(frame_student_details,
                                   text = student_dict[selected_student_id],
                                   bg='grey', fg='black', font=font_size)
        label_text.grid(row=0,column=0, columnspan=1, sticky='E')

        # display student total mark
        total_mark_text_for_feedback = ''
        label_text = tkinter.Label(frame_student_details,
                                   text = "Current Student's Marks:",
                                   bg='grey', fg='black', font=font_size)
        label_text.grid(row=1,column=0, columnspan=1)
        total_marks = 0
        assigment_total = 0
        for i_, question_number in enumerate(sorted(rubric_dict.keys())):
            temp_mark = (rubric_dict[question_number]['question_marks_weighted_array'] *
                            marks_dict[selected_student_id][question_number]['sub_criteria_mark_mask_array']).sum()
            total_marks += temp_mark
            assigment_total += rubric_dict[question_number]['question_total_mark']
            text_ = rubric_dict[question_number]['question_text'] + ' ({0:.2f}/{1:.2f})'.format(temp_mark,
                                                                  rubric_dict[question_number]['question_total_mark'])
            total_mark_text_for_feedback += text_ + '\n'
            label_text = tkinter.Label(frame_student_details,
                                       text=text_,
                                       bg='grey', fg='black', font=font_size)
            label_text.grid(row=2+i_, column=0, columnspan=1)

        label_text = tkinter.Label(frame_student_details,
                                   text='Total = {0:.2f}/{1:.2f}'.format(total_marks,assigment_total),
                                   bg='grey', fg='black', font=font_size)
        label_text.grid(row=2 + i_ + 1, column=0, columnspan=1)
        total_mark_text_for_feedback += 'Total = {0:.2f}/{1:.2f}'.format(total_marks,assigment_total)
        # update student's total grade
        marks_dict[selected_student_id]['total_grade'] = '{0:.2f}/{1:.2f}'.format(total_marks,assigment_total)


        # create feedback_button_list
        feedback_button_list = []
        for i_, feedback_text in enumerate(rubric_dict[selected_question]['question_feedbacks_list']):
            feedback_button_list.append(tkinter.Button(frame_feedback_selector,
                                                       text=feedback_text,
                                                       command=lambda arg_2=i_: update_feedback(arg_2),
                                                       bg='gray48', font=("Arial", student_id_font_size)))
            feedback_button_list[i_].grid(row=i_, column=0, sticky='W,E', columnspan=1)

            if marks_dict[selected_student_id][selected_question]['sub_criteria_feedback_mask_array'][i_]:
                feedback_button_list[i_].configure(bg='green')



        # feedback display
        feedback_display_text = create_question_feedback_text(selected_question, selected_student_id, current_mark)
        marks_dict[selected_student_id][selected_question]['feedback'] = feedback_display_text

        feedback_display = Text(frame_feedback_display, width = 130, height = 12, wrap = WORD)
        feedback_display.grid(row = 0, column = 0, columnspan = 10, sticky = W)
        feedback_display.insert('0.0', feedback_display_text)


        # custom feedback
        custom_feedback_display = Text(frame_custom_feedback_display, width = 105, height = 5, wrap = WORD)
        custom_feedback_display.grid(row = 0, column = 0, rowspan = 3, columnspan = 1, sticky = W)
        custom_feedback_display.insert('0.0', marks_dict[selected_student_id][selected_question]['custom_feedback'])

        custom_feedback_save_button = tkinter.Button(frame_custom_feedback_display,
                                                   text='Save extra feedback',
                                                   command=save_custom_feedback,
                                                   bg='blue', fg='white', font=("Arial", student_id_font_size))
        custom_feedback_save_button.grid(row=0, column=1, sticky='W', columnspan=1)

        add_feedback_option_button = tkinter.Button(frame_custom_feedback_display,
                                                   text='Add feedback option',
                                                   command=add_feedback_option,
                                                   bg='green', fg='white', font=("Arial", student_id_font_size))
        add_feedback_option_button.grid(row=1, column=1, sticky='W', columnspan=1)

        delete_feedback_option_button = tkinter.Button(frame_custom_feedback_display,
                                                   text='Delete feedback option',
                                                   command=delete_feedback_option,
                                                   bg='Red', fg='white', font=("Arial", student_id_font_size))
        delete_feedback_option_button.grid(row=2, column=1, sticky='W', columnspan=1)
    except BaseException as error_msg:
        error_handler('Error\n' + str(error_msg))

####################################################################################################
if __name__ == '__main__':
    # font size
    student_id_font_size = 10
    question_number_font_size = 16
    font_size = 12


    # clean exit program
    def clean_exit():
        if messagebox.askokcancel("Quit", "Do you really wish to quit?"):
            root.destroy()

    # program root
    root = Tk()

    # path_program = os.path.dirname(os.path.realpath(sys.argv[0]))
    path_program = ''
    path_input = path_program
    path_output = path_program

    # root.protocol("WM_DELETE_WINDOW", clean_exit)
    program_name = os.path.basename(__file__).split('_')[0]
    program_version = os.path.basename(__file__).split('_')[-1].split('.')[0]
    root_title = program_name + ' ' + program_version
    root.title(root_title)
    root.resizable(True,True)

    #start event loop
    app = Main_Window(root)

    # running your application, until you exit
    root.mainloop()

# from  U_Analysis_main import *
# pyinstaller --onefile --windowed U_Mark_V_0_05.py



