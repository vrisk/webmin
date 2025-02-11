#!/usr/local/bin/perl
# save_primary.cgi
# Save changes to primary zone options in named.conf
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
our (%access, %text, %in);

require './bind8-lib.pl';
&ReadParse();
&error_setup($text{'primary_err'});

my $zone = &get_zone_name_or_error($in{'zone'}, $in{'view'});
my $z = &zone_to_config($zone);
my $zconf = $z->{'members'};
my $dom = $zone->{'name'};
&can_edit_zone($zone) ||
	&error($text{'primary_ecannot'});
my $indent = $zone->{'view'} ? 2 : 1;

$access{'ro'} && &error($text{'primary_ero'});
$access{'opts'} || &error($text{'primary_eoptscannot'});
&lock_file(&make_chroot($z->{'file'}));

&save_choice("check-names", $z, $indent);
&save_choice("notify", $z, $indent);
&save_address("allow-update", $z, $indent);
&save_address("allow-transfer", $z, $indent);
&save_address("allow-query", $z, $indent);
&save_address("also-notify", $z, $indent);
&flush_file_lines();
&unlock_file(&make_chroot($z->{'file'}));
&webmin_log("opts", undef, $dom, \%in);
&redirect("edit_primary.cgi?zone=$in{'zone'}&view=$in{'view'}");

