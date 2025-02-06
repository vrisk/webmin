#!/usr/local/bin/perl
# edit_options.cgi
# Display options for an existing primary zone
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
our (%access, %text, %in); 

require './bind8-lib.pl';
&ReadParse();

my $zone = &get_zone_name_or_error($in{'zone'}, $in{'view'});
my $z = &zone_to_config($zone);
my $zconf = $z->{'members'};
my $dom = $zone->{'name'};
&can_edit_zone($zone) ||
	&error($text{'primary_ecannot'});

$access{'opts'} || &error($text{'primary_eoptscannot'});
&ui_print_header(&zone_subhead($zone), $text{'primary_opts'}, "",
		 undef, undef, undef, undef, &restart_links($zone));

# Start of form for editing zone options
print &ui_form_start("save_primary.cgi", "post");
print &ui_hidden("zone", $in{'zone'});
print &ui_hidden("view", $in{'view'});
print &ui_table_start($text{'primary_opts'}, "width=100%", 4);

print &choice_input($text{'primary_check'}, "check-names", $zconf,
		    $text{'warn'}, "warn", $text{'fail'}, "fail",
		    $text{'ignore'}, "ignore", $text{'default'}, undef);
print &choice_input($text{'primary_notify'}, "notify", $zconf,
		    $text{'yes'}, "yes", $text{'no'}, "no",
		    $text{'explicit'}, "explicit",
		    $text{'default'}, undef);

print &address_input($text{'primary_update'}, "allow-update", $zconf);
print &address_input($text{'primary_transfer'}, "allow-transfer", $zconf);

print &address_input($text{'primary_query'}, "allow-query", $zconf);
print &address_input($text{'primary_notify2'}, "also-notify", $zconf);

print &ui_table_end();
print &ui_form_end([ [ undef, $text{'save'} ] ]);

&ui_print_footer("edit_primary.cgi?zone=$in{'zone'}&view=$in{'view'}",
		 $text{'primary_return'});

