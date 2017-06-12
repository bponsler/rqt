/*
 * Copyright (c) 2011, Dirk Thomas, TU Darmstadt
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 *   * Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *   * Redistributions in binary form must reproduce the above
 *     copyright notice, this list of conditions and the following
 *     disclaimer in the documentation and/or other materials provided
 *     with the distribution.
 *   * Neither the name of the TU Darmstadt nor the names of its
 *     contributors may be used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 * ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

#ifndef rqt_gui_cpp__Plugin_H
#define rqt_gui_cpp__Plugin_H

#include <qt_gui_cpp/plugin.h>
#include <qt_gui_cpp/plugin_context.h>
#include <qt_gui_cpp/settings.h>

#include <rclcpp/node.hpp>

namespace rqt_gui_cpp {

/**
 * The base class for C++ plugins which use the ROS client library.
 * A plugin must not call ros::init() as this is performed once by the framework.
 * The name of the ROS node consists of the prefix "rqt_gui_cpp_node_" and the process id.
 */
class Plugin
  : public qt_gui_cpp::Plugin
  , public rclcpp::node::Node
{

public:

  Plugin()
    : qt_gui_cpp::Plugin(), rclcpp::node::Node("rqt_gui")
  {}

  /**
   * Shutdown and clean up the plugin before unloading.
   * I.e. unregister subscribers and stop timers.
   */
  virtual void shutdownPlugin()
  {}

private:

  void onInit()
  {}

};

} // namespace

#endif // rqt_gui_cpp__Plugin_H
