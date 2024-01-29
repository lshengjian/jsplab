# from jsplab import FJSP_Data, JSP_Data, OperateType
# from jsplab.utils import InstanceFJSP
# from pathlib import Path
# data0 = '''2 3 1
# 2 2 1 1 2 2 1 3 3
# 1 3 1 1 2 2 3 3'''


# def test_text2matrix():
#     data = filter(lambda x: len(x) > 0, data0.split('\n'))
#     data = list(data)
#     fjsp = InstanceFJSP('demo')
#     fjsp.parse(data)

#     num_tasks, op_times = fjsp.data.num_tasks, fjsp.data.op_times
#     assert len(num_tasks) == 2
#     assert op_times.shape == (3, 3)

#     assert list(op_times[0]) == [1, 2, 0]  # job1
#     assert list(op_times[1]) == [0, 0, 3]  # job1
#     assert list(op_times[2]) == [1, 2, 3]  # job2


# def test_matrix2text():
#     data = filter(lambda x: len(x) > 0, data0.split('\n'))
#     data = list(data)
#     fjsp = InstanceFJSP('demo')
#     fjsp.parse(data)

#     assert fjsp.to_text(',') == data0.replace(' ', ',')
