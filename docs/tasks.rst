.. Copyright (c) 2015 Pietro Albini <pietro@pietroalbini.io>
   Released under the MIT license

.. _tasks:

~~~~~~~~~~~~~~~~~~~~~~~~~
Execute indipendent tasks
~~~~~~~~~~~~~~~~~~~~~~~~~

Unfortunately, not everything can be executed after an user input, especially
if you need periodic execution, or background cleanup. In order to solve this,
botogram provides you the tasks system, which allows the execution of
indipended tasks.

.. _tasks-repeated:

==================
Repeated execution
==================

There might be the case when you need to execute a specific function
periodically. For example if you want to implement alerts, or if you need to do
some internal cleanup in your bot. Timers offers an easy and reliable way to
implement this, with a resolution of one second. Just use the
:py:meth:`~botogram.Bot.timer` decorator:

.. code-block:: python

   @bot.init_shared_memory
   def init(shared):
       shared["subs"] = []

   @bot.command("subscribe")
   @botogram.pass_shared
   def subscribe_command(shared, chat, message, args):
       """Subscribe to the hourly BONG"""
       subs = shared["subs"]
       subs.append(chat.id)
       shared["subs"] = subs

   @bot.timer(3600)
   @botogram.pass_bot
   @botogram.pass_shared
   def BONG(bot, shared):
       for chat in shared["subs"]:
           bot.send(chat, "BONG")

If you're working with components, you can instead use the
:py:meth:`~botogram.Component.add_timer` method of the component instance.
