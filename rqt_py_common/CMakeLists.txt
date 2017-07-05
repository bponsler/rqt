cmake_minimum_required(VERSION 3.5)
project(rqt_py_common)

# Add support for C++11
if(NOT WIN32)
  add_definitions(-std=c++11)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rosidl_default_generators REQUIRED)

ament_python_install_package(${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(std_msgs REQUIRED)

  rosidl_generate_interfaces(${PROJECT_NAME}
    "test/msg/ArrayVal.msg"
    "test/msg/Val.msg"
    DEPENDENCIES std_msgs)
endif()

install(DIRECTORY resource
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_cmake_nose REQUIRED)
  ament_add_nose_test(${PROJECT_NAME}_nose_tests test)
  set_tests_properties(${PROJECT_NAME}_nose_tests PROPERTIES DEPENDS ${PROJECT_NAME})
endif()

ament_export_dependencies(ament_cmake)
ament_export_dependencies(ament_cmake_python)
ament_export_include_directories(${INCLUDE_DIRS})

ament_package()
