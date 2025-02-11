#!/usr/local/bin/perl
# Re-generate the zone key and re-sign a zone
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
our (%text, %in);

require './bind8-lib.pl';
&error_setup($text{'resign_err'});
&ReadParse();
my $zone = &get_zone_name_or_error($in{'zone'}, $in{'view'});
my $dom = $zone->{'name'};
&can_edit_zone($zone) ||
	&error($text{'primary_ecannot'});

# Do the signing
&lock_file(&make_chroot(&absolute_path($zone->{'file'})));
my $err = &resign_dnssec_key($zone);
&error($err) if ($err);
&unlock_file(&make_chroot(&absolute_path($zone->{'file'})));

# Return to primary page
&webmin_log("resign", undef, $dom);
&redirect("edit_primary.cgi?zone=$in{'zone'}&view=$in{'view'}");

