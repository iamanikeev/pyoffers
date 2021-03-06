# coding: utf-8
import pytest

from pyoffers.exceptions import HasOffersException
from pyoffers.models import Advertiser, AffiliateOffer, Conversion, Country, Offer, OfferCategory, OfferFile


CASSETTE_NAME = 'offer'


def test_create_success(offer):
    assert isinstance(offer, Offer)
    assert offer.offer_url == 'http://www.example.com'


def test_find_by_id_success(api, offer):
    instance = api.offers.find_by_id(offer.id)
    assert isinstance(instance, Offer)
    assert instance.offer_url == offer.offer_url


def test_find_by_id_fail(api):
    assert api.offers.find_by_id(1000) is None


def test_find_all(api):
    result = api.offers.find_all(limit=2)
    assert len(result) == 2
    assert all(isinstance(item, Offer) for item in result)


def test_get_target_countries(api):
    result = api.offers.get_target_countries(id=46)
    assert len(result) == 1
    assert all(isinstance(item, Country) for item in result)


def test_get_target_countries_empty(offer):
    assert offer.get_target_countries() == []


def test_update_success(offer):
    new_instance = offer.update(offer_url='test.com')
    assert new_instance.offer_url == 'http://test.com'
    assert new_instance == offer


def test_add_target_country_success(offer):
    assert offer.add_target_country('ES') is True


def test_add_category_success(offer):
    assert offer.add_category(1) is True


def test_get_categories(offer):
    categories = offer.get_categories()
    assert len(categories) == 1
    assert isinstance(categories[0], OfferCategory)


def test_update_category(offer):
    assert offer.get_categories()[0].update(status='deleted') is True


def test_add_category_fail(offer):
    with pytest.raises(HasOffersException) as exc:
        offer.add_category(-1)
    assert str(exc.value) == 'Row id is negative'


def test_block_affiliate_success(offer):
    assert offer.block_affiliate(1) is True


def test_block_affiliate_fail(offer):
    with pytest.raises(HasOffersException) as exc:
        offer.block_affiliate(21)
    assert str(exc.value) == 'Failed to hydrate rows: 21'


class TestContain:

    def test_find_all(self, api):
        offer = api.offers.find_all(id=62, contain=['Country'])[0]
        assert isinstance(offer, Offer)
        assert offer.country.id == '724'

    def test_find_all_empty_related(self, api):
        offers = api.offers.find_all(currency='CZK', contain=['Country'])
        assert offers[0].country is None
        assert offers[1].country.id == '203'

    def test_find_by_id(self, api):
        offer = api.offers.find_by_id(id=62, contain=['Country'])
        assert isinstance(offer, Offer)
        assert offer.country.id == '724'

    def test_find_by_id_array_related(self, api):
        offer = api.offers.find_by_id(438, contain=['Country'])
        assert isinstance(offer, Offer)
        assert isinstance(offer.country, list)
        assert isinstance(offer.country[0], Country)

    def test_find_by_id_single_instance(self, api):
        offer = api.offers.find_by_id(438, contain=['Advertiser'])
        assert isinstance(offer.advertiser, Advertiser)


def test_find_all_ids(api):
    results = api.offers.find_all_ids()
    assert isinstance(results, list)
    assert all(result.isdigit() for result in results)


def test_conversions_manager(offer):
    conversions = offer.conversions.find_all()
    assert len(conversions) == 1
    assert isinstance(conversions[0], Conversion)
    assert conversions[0].offer_id == offer.id


def test_files_manager(offer):
    files = offer.files.find_all()
    assert len(files) == 1
    assert isinstance(files[0], OfferFile)
    assert files[0].offer_id == offer.id


def test_get_offer_files_with_creative_code(offer):
    files = offer.get_offer_files_with_creative_code(20)
    assert len(files) == 1
    assert isinstance(files[0], OfferFile)
    assert files[0].offer_id == offer.id
    assert files[0].creativecode == 'http://www.example.com'


def test_set_affiliate_approval_status(api):
    assert api.offers.set_affiliate_approval_status(472, 20, 'approved') is True


def test_offer_set_affiliate_approval_status(offer):
    assert isinstance(offer.set_affiliate_approval_status(20, 'approved'), AffiliateOffer)
    assert isinstance(offer.set_affiliate_approval_status(20, 'approved'), bool)


def test_get_affiliate_approval_status(offer):
    assert offer.get_affiliate_approval_status(20) == 'approved'


def test_get_blocked_affiliate_ids(offer):
    assert isinstance(offer.get_blocked_affiliate_ids(), list)


def test_get_approved_affiliate_ids(offer):
    assert isinstance(offer.get_approved_affiliate_ids(), list)


def test_get_unapproved_affiliate_ids(offer):
    assert isinstance(offer.get_unapproved_affiliate_ids(), list)


def test_unblock_affiliate(offer):
    assert offer.unblock_affiliate(20) is True


def test_generate_tracking_link(offer):
    result = offer.generate_tracking_link(94, file_id=727)
    assert 'offer_id=472' in result['click_url']


def test_generate_tracking_link_w_tiny_url(offer):
    result = offer.generate_tracking_link(94, file_id=727, tiny_url=True)
    assert 'offer_id=472' not in result['click_url']


def test_find_all_affiliate_approvals(offer):
    result = offer.find_all_affiliate_approvals()
    assert isinstance(result, list)
    assert all(isinstance(item, AffiliateOffer) for item in result)
    assert len(set(item.offer_id for item in result)) == 1  # Check that all results have the same offer_id
