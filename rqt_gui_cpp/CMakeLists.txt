cmake_minimum_required(VERSION 3.5)
project(rqt_gui_cpp)

# Add support for C++11
if(NOT WIN32)
  add_definitions(-std=c++11)
endif()

find_package(ament_cmake REQUIRED)
#find_package(qt_gui REQUIRED)
find_package(qt_gui_cpp REQUIRED)
find_package(rclcpp REQUIRED)

set(INCLUDE_DIRS include ${ament_cmake_INCLUDE_DIRS} ${qt_gui_INCLUDE_DIRS}
  ${qt_gui_cpp_INCLUDE_DIRS} ${rclcpp_INCLUDE_DIRS})
include_directories(${INCLUDE_DIRS})

set(LIBRARY_DIRS ${ament_cmake_LIBRARY_DIRS} ${qt_gui_LIBRARY_DIRS}
  ${qt_gui_cpp_LIBRARY_DIRS} ${rclcpp_LIBRARY_DIRS})

link_directories(${LIBRARY_DIRS})

set(LIBS ${ament_cmake_LIBRARIES} ${qt_gui_LIBRARIES} ${qt_gui_cpp_LIBRARIES}
  ${rclcpp_LIBRARIES})

# Load catkin and all dependencies required for this package

find_package(Qt5Widgets REQUIRED)

set(rqt_gui_cpp_SRCS src/rqt_gui_cpp/nodelet_plugin_provider.cpp
  src/rqt_gui_cpp/roscpp_plugin_provider.cpp)

set(rqt_gui_cpp_HDRS src/rqt_gui_cpp/roscpp_plugin_provider.h)

qt5_wrap_cpp(rqt_gui_cpp_MOCS ${rqt_gui_cpp_HDRS})

add_library(${PROJECT_NAME} ${rqt_gui_cpp_SRCS} ${rqt_gui_cpp_MOCS})
target_link_libraries(${PROJECT_NAME} ${LIBS} Qt5::Widgets)

if(APPLE)
  set_target_properties(${PROJECT_NAME}
    PROPERTIES
    LINK_FLAGS "-undefined dynamic_lookup")
endif()

install(FILES plugin.xml DESTINATION share/${PROJECT_NAME})

install(TARGETS ${PROJECT_NAME}
  ARCHIVE
  DESTINATION lib
  LIBRARY
  DESTINATION lib)

install(DIRECTORY include/${PROJECT_NAME}/
  DESTINATION include/${PROJECT_NAME})

ament_export_dependencies(ament_cmake)
ament_export_dependencies(qt_gui)
ament_export_dependencies(qt_gui_cpp)
ament_export_dependencies(rclcpp)
ament_export_include_directories(${INCLUDE_DIRS})
ament_export_libraries(${PROJECT_NAME} ${LIBS})

ament_package()
