#!/usr/local/bin/perl
# Sign a primary zone
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
our (%access, %text, %in);

require './bind8-lib.pl';
&error_setup($text{'sign_err'});
&ReadParse();
my $zone = &get_zone_name_or_error($in{'zone'}, $in{'view'});
my $dom = $zone->{'name'};
&can_edit_zone($zone) ||
	&error($text{'primary_ecannot'});

# Do the signing
&lock_file(&make_chroot(&absolute_path($zone->{'file'})));
my $err = &sign_dnssec_zone($zone, 1);
&error($err) if ($err);
&unlock_file(&make_chroot(&absolute_path($zone->{'file'})));
$err = &restart_zone($zone->{'name'}, $zone->{'view'});
&error($err) if ($err);

# Return to primary page
&webmin_log("sign", undef, $dom);
&redirect("edit_master.cgi?zone=$in{'zone'}&view=$in{'view'}");

