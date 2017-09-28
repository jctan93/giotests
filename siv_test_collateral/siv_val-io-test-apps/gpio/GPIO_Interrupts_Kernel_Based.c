#include <linux/module.h>
#include <linux/init.h>
#include <linux/irq.h>
#include <linux/interrupt.h>
#include <linux/gpio.h>

static int irq;
static int GPIO = 113;
static int TYPE = 0;
module_param(GPIO, int, S_IRUGO);
module_param(TYPE, int, S_IRUGO);

static irqreturn_t gpio_reset_interrupt(int irq, void* dev_id) {
        printk(KERN_ERR "GPIO_Interrupt: gpio0 IRQ %d event \n", irq);
        return(IRQ_HANDLED);
}


static int __init mymodule_init(void) {
        irq = gpio_to_irq(GPIO);

		switch(TYPE){
			case 0:
				if ( request_irq(irq, gpio_reset_interrupt, IRQF_TRIGGER_NONE|IRQF_ONESHOT, "gpio_reset", NULL) ) {
						printk(KERN_ERR "GPIO_RESET: trouble requesting IRQ %d \n",irq);
						return(-EIO);
				} else {
						printk(KERN_ERR "GPIO_RESET: requesting NONE IRQ %d-> fine\n",irq);
				}
				break;
			case 1:
				if ( request_irq(irq, gpio_reset_interrupt, IRQF_TRIGGER_RISING|IRQF_ONESHOT, "gpio_reset", NULL) ) {
						printk(KERN_ERR "GPIO_RESET: trouble requesting IRQ %d \n",irq);
						return(-EIO);
				} else {
						printk(KERN_ERR "GPIO_RESET: requesting EDGE_RISE IRQ %d-> fine\n",irq);
				}
				break;
			case 2:
				if ( request_irq(irq, gpio_reset_interrupt, IRQF_TRIGGER_FALLING|IRQF_ONESHOT, "gpio_reset", NULL) ) {
						printk(KERN_ERR "GPIO_RESET: trouble requesting IRQ %d \n",irq);
						return(-EIO);
				} else {
						printk(KERN_ERR "GPIO_RESET: requesting EDGE_FALL IRQ %d-> fine\n",irq);
				}
				break;
			case 3:
				if ( request_irq(irq, gpio_reset_interrupt, IRQF_TRIGGER_HIGH|IRQF_ONESHOT, "gpio_reset", NULL) ) {
						printk(KERN_ERR "GPIO_RESET: trouble requesting IRQ %d \n",irq);
						return(-EIO);
				} else {
						printk(KERN_ERR "GPIO_RESET: requesting LEVEL_HIGH IRQ %d-> fine\n",irq);
				}
				break;
			case 4:
				if ( request_irq(irq, gpio_reset_interrupt, IRQF_TRIGGER_LOW|IRQF_ONESHOT, "gpio_reset", NULL) ) {
						printk(KERN_ERR "GPIO_RESET: trouble requesting IRQ %d \n",irq);
						return(-EIO);
				} else {
						printk(KERN_ERR "GPIO_RESET: requesting LEVEL_LOW IRQ %d-> fine\n",irq);
				}
				break;
			default:
				printk(KERN_ERR "GPIO_RESET: Invalid Type \n");
				break;
		}
		


		printk("GPIO_Interrupt Mounted: %d \n", GPIO);
		
        return 0;
}

static void __exit mymodule_exit(void) {
		disable_irq(irq);
        free_irq(irq, NULL);
        printk ("GPIO_RESET: module unloaded \n");
        return;
}

module_init(mymodule_init);
module_exit(mymodule_exit);

MODULE_LICENSE("GPL");