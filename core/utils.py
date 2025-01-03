import matplotlib.pyplot as plt
import base64
from io import BytesIO


def get_graph():
    buffer = BytesIO() # byte buffer for the image to be saved to
    plt.savefig(buffer, format='png')
    buffer.seek(0) # set the cursor to the beginning of the string 
    image_png = buffer.getvalue() # retrieve the entire file content
    print(image_png)
    graph = base64.b64encode(image_png) # encode a byte-like object
    print(graph)
    decoded_graph = graph.decode('utf-8') # decode the string from base64 to utf-8
    print(decoded_graph)
    buffer.close()
    return decoded_graph


def get_plot(x, y):
    plt.switch_backend('AGG')
    plt.figure(figure=(10,5))
    plt.title('Yearly Income Review')
    plt.plot(x, y)
    plt.xticks(rotation=45)
    plt.xlabel('months')
    plt.ylabel('amount')
    plt.tight_layout()
    graph = get_graph()
    return graph


# def plan_interval(interval):
#     match interval:
#         case 'weekly':
#             return Response({"message": "WEEKLY plan created successfully. Thank you.",
#                                 'create_plan':create_plan},
#                                 status=create_plan['status'])
#         case 'monthly':
#             return Response({"message": "MONTHLY plan created successfully. Thank you.",
#                                 'create_plan':create_plan},
#                                 status=create_plan['status'])
#         case 'quarterly':
#             return Response({"message": "QUARTERLY plan created successfully. Thank you.",
#                                 'create_plan':create_plan},
#                                 status=create_plan['status'])
#         case 'biannually':
#             return Response({"message": "BIANNUALLY plan created successfully. Thank you.",
#                                 'create_plan':create_plan},
#                                 status=create_plan['status'])
#         case 'annually':
#             return Response({"message": "ANNUALLY plan created successfully. Thank you.",
#                                 'create_plan':create_plan},
#                                 status=status.HTTP_201_CREATED)
#         case _:
#             return Response({"message": "Invalid plan. Please try again.",
#                                 'create__plan':create_plan},
#                                 status=create_plan['status'])