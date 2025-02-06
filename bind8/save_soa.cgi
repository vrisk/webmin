#!/usr/local/bin/perl
# save_soa.cgi
# Save changes to an SOA record
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
our (%access, %text, %in, %config);

require './bind8-lib.pl';
&ReadParse();
&error_setup($text{'primary_err2'});
my $zone = &get_zone_name_or_error($in{'zone'}, $in{'view'});
my $dom = $zone->{'name'};
&can_edit_zone($zone) ||
	&error($text{'primary_ecannot'});
$access{'ro'} && &error($text{'primary_ero'});
$access{'params'} || &error($text{'primary_esoacannot'});

# Get the SOA and file
my @recs = &read_zone_file($zone->{'file'}, $dom);
my $soa;
foreach my $r (@recs) {
	$soa = $r if ($r->{'type'} eq "SOA");
	}
$soa || &error($text{'primary_esoagone'});
my $file = $soa->{'file'};

# check inputs
&valdnsname($in{'primary'}, 0, $in{'origin'}) ||
	&error(&text('primary_eprimary', $in{'primary'}));
&valemail($in{'email'}) ||
	&error(&text('primary_eemail', $in{'email'}));
$in{'refresh'} =~ /^\d+$/ ||
	&error(&text('primary_erefresh', $in{'refresh'}));
$in{'retry'} =~ /^\d+$/ ||
	&error(&text('primary_eretry', $in{'retry'}));
$in{'expiry'} =~ /^\d+$/ ||
	&error(&text('primary_eexpiry', $in{'expiry'}));
$in{'minimum'} =~ /^\d+$/ ||
	&error(&text('primary_eminimum', $in{'minimum'}));
if ($in{'email'} =~ /\@/) {
	$in{'email'} = &email_to_dotted($in{'email'});
	}
$in{'defttl_def'} || $in{'defttl'} =~ /^\d+$/ ||
	&error(&text('primary_edefttl', $in{'defttl'}));

&lock_file(&make_chroot($file));
@recs = &read_zone_file($file, $in{'origin'});
my $old = $recs[$in{'num'}];
# already set serial if no acl allow it to update or update is disabled
my $serial = $old->{'values'}->[2];
if ($config{'updserial_on'}) {
	# automatically handle serial numbers ?
	$serial = &compute_serial($old->{'values'}->[2]);
	}
else {
	$in{'serial'} =~ /^\d+$/ || &error($text{'primary_eserial'});
	$serial = $in{'serial'};
	}
my $vals = "$in{'primary'} $in{'email'} (\n".
	"\t\t\t$serial\n".
	"\t\t\t$in{'refresh'}$in{'refunit'}\n".
	"\t\t\t$in{'retry'}$in{'retunit'}\n".
	"\t\t\t$in{'expiry'}$in{'expunit'}\n".
	"\t\t\t$in{'minimum'}$in{'minunit'} )";
&modify_record($file, $old, $old->{'name'}, $old->{'ttl'},
	       $old->{'class'}, "SOA", $vals);

my ($defttl) = grep { $_->{'defttl'} } @recs;
if (!$defttl && !$in{'defttl_def'}) {
	&create_defttl($file, $in{'defttl'}.$in{'defttlunit'});
	}
elsif ($defttl && !$in{'defttl_def'}) {
	&modify_defttl($file, $defttl, $in{'defttl'}.$in{'defttlunit'});
	}
elsif ($defttl && $in{'defttl_def'}) {
	&delete_defttl($file, $defttl);
	}

&unlock_file(&make_chroot($file));
&webmin_log("soa", undef, $in{'origin'}, \%in);
&redirect("edit_primary.cgi?zone=$in{'zone'}&view=$in{'view'}");

