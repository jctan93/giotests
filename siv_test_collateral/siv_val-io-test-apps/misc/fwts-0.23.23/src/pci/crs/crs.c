/*
 * Copyright (C) 2010-2011 Canonical
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 *
 */

#include "fwts.h"

static int crs_get_bios_date(fwts_framework *fw, int *day, int *mon, int *year)
{
	fwts_list *dmi_text;
	fwts_list_link *item;
	char buffer[PATH_MAX+256];

	*day = 0;
	*mon = 0;
	*year = 0;

	snprintf(buffer, sizeof(buffer), "%s -t 0", fw->dmidecode);
	if (fwts_pipe_exec(buffer, &dmi_text)) {
		fwts_log_error(fw, "Failed to execute dmidecode.");
		return FWTS_ERROR;
	}

	if (dmi_text == NULL) {
		fwts_log_error(fw,
			"Failed to read output from dmidecode (out of memory).");
		return FWTS_ERROR;
	}

	fwts_list_foreach(item, dmi_text) {
		char *ptr;
		char *text = fwts_text_list_text(item);
		char *pattern = "Release Date: ";
		if ((ptr = strstr(text, pattern)) != NULL) {
			ptr += strlen(pattern);
			sscanf(ptr, "%d/%d/%d", mon, day, year);
			break;
		}
	}
	fwts_list_free(dmi_text, free);

	return FWTS_OK;
}

static int crs_test1(fwts_framework *fw)
{
	fwts_list *klog;
	int day, mon, year;
	char *cmdline;

	if ((cmdline = fwts_get("/proc/cmdline")) == NULL) {
		fwts_log_error(fw, "Cannot read /proc/cmdline");
		return FWTS_ERROR;
	}

	if (crs_get_bios_date(fw, &day, &mon, &year) != FWTS_OK) {
		fwts_log_error(fw, "Cannot determine age of BIOS.");
		return FWTS_ERROR;
	}

	if ((klog = fwts_klog_read()) == NULL) {
		fwts_log_error(fw, "Cannot read kernel log.");
		return FWTS_ERROR;
	}

        if (fwts_klog_regex_find(fw, klog,
		"PCI: Ignoring host bridge windows from ACPI;") > 0) {
		if (strstr(cmdline, "pci=nocrs") != NULL) {
			fwts_skipped(fw, "Kernel was booted with pci=nocrs, Ignoring host bridge windows _CRS settings from ACPI, skipping test.");
		}
		else {
			if (year == 0) {
				fwts_failed(fw, LOG_LEVEL_MEDIUM,
					"BIOSTooOld",
					"The kernel could not determine the BIOS age "
					"and has assumed that your BIOS is too old to correctly "
					"specify the host bridge MMIO aperture using _CRS.");
				fwts_tag_failed(fw, FWTS_TAG_BIOS);
				fwts_log_advice(fw, "You can override this by booting with \"pci=use_crs\".");

			} else if (year < 2008) {
				fwts_passed(fw,
					"The kernel has detected an old BIOS (%d/%d/%d) "
					"and has assumed that your BIOS is too old to correctly "
					"specify the host bridge MMIO aperture using _CRS.", mon, day, year);
				fwts_tag_failed(fw, FWTS_TAG_BIOS);
				fwts_log_advice(fw, "You can override this by booting with \"pci=use_crs\".");
			} else {
				fwts_failed(fw, LOG_LEVEL_MEDIUM,
					"HostBridgeWindows",
					"The kernel is ignoring host bridge windows from ACPI for some unknown reason. "
					"pci=nocrs has not been used as a boot parameter and the BIOS may be recent enough "
					"to support this (%d/%d/%d)", mon, day, year);
				fwts_tag_failed(fw, FWTS_TAG_BIOS);
			}
		}
	} else if (fwts_klog_regex_find(fw, klog, "PCI: Using host bridge windows from ACPI;") > 0) {
		if (strstr(cmdline, "pci=use_crs") != NULL) {
			if (year == 0)  {
				fwts_failed(fw, LOG_LEVEL_MEDIUM,
					"BIOSNoReleaseDate",
					"The BIOS does not seem to have release date, hence pci=use_crs was required.");
				fwts_tag_failed(fw, FWTS_TAG_BIOS);
			} else if (year < 2008) {
				fwts_passed(fw,
					"The BIOS is relatively old (%d/%d/%d) and hence pci=use_crs was required to "
					"enable host bridge windows _CRS settings from ACPI.", mon, day, year);
				fwts_tag_failed(fw, FWTS_TAG_BIOS);
			} else {
				fwts_failed(fw, LOG_LEVEL_LOW,
					"BIOSSupportBridgeWindows",
					"Kernel was booted with pci=use_crs but this may be uncessary as "
					"the BIOS is new enough to support automatic bridge windows configuring using _CRS from ACPI. "
					"However, the workaround may be necessary because _CRS is incorrect or not implemented in the "
					"DSDT.");
				fwts_tag_failed(fw, FWTS_TAG_BIOS);
			}
		}
		else {
			fwts_passed(fw,
				"The kernel has detected a BIOS newer than the end of 2007 (%d/%d/%d) "
				"and has assumed that your BIOS can correctly "
				"specify the host bridge MMIO aperture using _CRS.  If this does not work "
				"correctly you can override this by booting with \"pci=nocrs\".", mon, day, year);
		}
	} else {
		fwts_skipped(fw, "Cannot find host bridge message in kernel log, skipping test.");
	}

	fwts_list_free(klog, free);
	free(cmdline);

	return FWTS_OK;
}

static fwts_framework_minor_test crs_tests[] = {
	{ crs_test1, "Check PCI host bridge configuration using _CRS." },
	{ NULL, NULL },
};

static fwts_framework_ops crs_ops = {
	.description = "Check PCI host bridge configuration using _CRS.",
	.minor_tests = crs_tests
};

FWTS_REGISTER(crs, &crs_ops, FWTS_TEST_ANYTIME, FWTS_BATCH | FWTS_ROOT_PRIV);
