/*
 * gpio_test.c: GPIO test program for Intel Platforms which uses
 * 		Designware-based SIO such as Baytrail.
 *
 * Copyright (c) 2015, Intel Corporation.
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms and conditions of the GNU General Public License,
 * version 2, as published by the Free Software Foundation.
 *
 * This program is distributed in the hope it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
 * more details.
 *
 */
/*
 *  This program is free software; you can redistribute it and/or
 *  modify it under the terms of the GNU General Public License
 *  as published by the Free Software Foundation; either version 2
 *  of the License, or (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 */
/*
 This is like all programs in the Linux Programmer's Guide meant
 as a simple practical demonstration.
 It can be used as a base for a real terminal program.
 */

#include <linux/module.h>
#include <linux/kthread.h>
#include <linux/delay.h>
#include <linux/init.h>
#include <linux/gpio.h>
#include <linux/sched.h>
#include <linux/slab.h>

//	GPIO pins on Bakersport/Bayleybay board that can be used for testing:-
//	GPIO_S5[08] - P90
//	GPIO_S5[09] - P91
//	GPIO_S5[10] - P92
//	GPIO_S0_SC[055] - P209

//	GPIO pin # can be changed according to target board
#define GPIO_PIN1	92		//for Bakersport or Bayleybay board
#define GPIO_PIN2	209		//for Bakersport or Bayleybay board

#define	SLEEP_US	(500)
#define	SLEEP_US2	(600)

/* Task handler to identify thread. */
struct task_struct *task1;
struct task_struct *task2;
int data;
int sw = 0;
int	loop = 1;

void gpio_test_init(void) 
{
	/* Request GPIO Resources */
	if (gpio_request(GPIO_PIN1, "GPIO-Output") < 0)
		printk("Invalid request for GPIO Pin %d\n", GPIO_PIN1);
	if (gpio_request(GPIO_PIN2, "GPIO-Output") < 0)
		printk("Invalid request for GPIO Pin %d\n", GPIO_PIN2);

	/* Set GPIO direction */
	if (gpio_direction_output(GPIO_PIN1, 0) < 0)
		printk("Invalid setting direction for GPIO Pin %d\n", GPIO_PIN1);
	if (gpio_direction_output(GPIO_PIN2, 0) < 0)
		printk("Invalid setting direction for GPIO Pin %d\n", GPIO_PIN2);
}

void gpio_test_release(void) 
{
	gpio_free(GPIO_PIN1);
	gpio_free(GPIO_PIN2);
}


int thread_function_one(void *data)
{
	int cpu;
	int ret = 10;
	int readback_value;

	printk(KERN_INFO "IN THREAD FUNCTION 1 \n");
	cpu = get_cpu();
	put_cpu();
	printk("t1 cpu = %d\n",cpu);

	while (loop)	{
		if (kthread_should_stop())
			break;

		gpio_set_value(GPIO_PIN1, sw);					// write '0' or '1' to GPIO_PIN1
		readback_value = gpio_get_value(GPIO_PIN1);		// read back the data from GPIO_PIN1
		if (readback_value != sw)
		{
			printk(KERN_INFO "Value = %d. Real Time Value = %d. GPIO-%d write data failed!!!!!.\n", sw, readback_value, GPIO_PIN1);
			loop = 0;
		}
		sw ^= 1;										// toggle data (to create square pulse every SLEEP_US time
		usleep_range(SLEEP_US, SLEEP_US + 1);
	}
	printk(KERN_INFO "EXIT from thread function 1\n");
	do_exit(0);
	return ret;
}

int thread_function_two(void *data)
{
	int cpu;
	int ret = 10;
	int i_value;

	printk(KERN_INFO "IN THREAD FUNCTION 2 \n");
	cpu = get_cpu();
	put_cpu();
	printk("t2 cpu = %d\n",cpu);

	while (loop)	{
		if (kthread_should_stop())
			break;
		i_value = gpio_get_value(GPIO_PIN2);			// read data from GPIO_PIN2	every SLEEP_US2 time
		usleep_range(SLEEP_US2, SLEEP_US2 + 1);
	}
	printk(KERN_INFO "EXIT from thread function 2\n");
	do_exit(0);
	return ret;
}

static int kernel_init(void)
{
	int cpu;
	printk(KERN_INFO "module_init\n");

	cpu = get_cpu();
	put_cpu();
	printk("main thread cpu = %d \n",cpu);

	gpio_test_init();

	task1 = kthread_create(&thread_function_one,(void *)&data,"one");
	kthread_bind(task1, cpu);
	wake_up_process(task1);

	cpu = 2;
	task2 = kthread_create(&thread_function_two,(void *)&data,"two");
	kthread_bind(task2, cpu);
	wake_up_process(task2);

	
	return 0;
}

static void kernel_exit(void)
{
	loop = 0;
	gpio_test_release();

	printk(KERN_INFO "module_exit\n");
	return;
}

module_init(kernel_init);
module_exit(kernel_exit);

MODULE_LICENSE("GPL");