#!/usr/local/bin/perl
# edit_soptions.cgi
# Display options for an existing secondary or stub zone
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
our (%access, %in, %text);
our $scriptname;

require './bind8-lib.pl';
&ReadParse();

my $zone = &get_zone_name_or_error($in{'zone'}, $in{'view'});
my $z = &zone_to_config($zone);
my $zconf = $z->{'members'};
my $dom = $zone->{'name'};
&can_edit_zone($zone) ||
	&error($text{'primary_ecannot'});

$access{'opts'} || &error($text{'secondary_ecannot'});
&ui_print_header(&zone_subhead($zone), $text{'primary_opts'}, "",
		 undef, undef, undef, undef, &restart_links($zone));

# Start of the form
print &ui_form_start("save_secondary.cgi", "post");
print &ui_hidden("zone", $in{'zone'});
print &ui_hidden("view", $in{'view'});
print &ui_hidden("secondary_stub", $scriptname);
print &ui_table_start($text{'secondary_opts'}, "width=100%", 2);

# primary addresses and port
print &address_port_input($text{'secondary_primaries'},
			  $text{'secondary_primaryport'},
			  $text{'secondary_primary_port'}, 
			  $text{'default'}, 
			  "primaries",
			  "port",
			  $zconf,
			  5);

# Transfer time max
print &opt_input($text{'secondary_max'}, "max-transfer-time-in",
		 $zconf, $text{'default'}, 4, $text{'secondary_mins'});

# secondary records file
print &opt_input($text{'secondary_file'}, "file", $zconf, $text{'secondary_none'}, 80);

print &choice_input($text{'secondary_check'}, "check-names", $zconf,
		    $text{'warn'}, "warn", $text{'fail'}, "fail",
		    $text{'ignore'}, "ignore", $text{'default'}, undef);
print &choice_input($text{'secondary_notify'}, "notify", $zconf,
		    $text{'yes'}, "yes", $text{'no'}, "no",
		    $text{'explicit'}, "explicit",
		    $text{'default'}, undef);
print &choice_input($text{'secondary_format'}, "primaryfile-format", $zconf,
		    $text{'secondary_raw'}, "raw", $text{'secondary_text'}, "text",
		    $text{'default'}, undef);

print &addr_match_input($text{'secondary_update'}, "allow-update", $zconf);
print &addr_match_input($text{'secondary_transfer'}, "allow-transfer", $zconf);

print &addr_match_input($text{'secondary_query'}, "allow-query", $zconf);
print &address_input($text{'secondary_notify2'}, "also-notify", $zconf);

print &ui_table_end();
print &ui_form_end([ [ undef, $text{'save'} ] ]);

&ui_print_footer("edit_secondary.cgi?zone=$in{'zone'}&view=$in{'view'}",
		 $text{'primary_return'});

