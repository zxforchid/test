# coding=utf-8

# data loader
import torch
from skimage import io, transform, color
import numpy as np
import math
from torch.utils.data import Dataset


# ==========================dataset load==========================
class RescaleT(object):

	def __init__(self, output_size):
		assert isinstance(output_size, (int, tuple))
		self.output_size = output_size

	def __call__(self, sample):
		image, label, edge = sample['image'], sample['label'], sample['edge']
		# resize the image to (self.output_size, self.output_size) and convert image from range [0,255] to [0,1]
		img = transform.resize(image, (self.output_size, self.output_size), mode='constant')
		lbl = transform.resize(label, (self.output_size, self.output_size), mode='constant', order=0, preserve_range=True)
		edge = transform.resize(edge, (self.output_size, self.output_size), mode='constant', order=0, preserve_range=True)

		return {'image': img, 'label': lbl, 'edge': edge}


class Rescale(object):

	def __init__(self, output_size):
		assert isinstance(output_size, (int, tuple))
		self.output_size = output_size

	def __call__(self, sample):
		image, label, edge = sample['image'], sample['label'], sample['edge']

		h, w = image.shape[:2]

		if isinstance(self.output_size, int):
			if h > w:
				new_h, new_w = self.output_size*h/w, self.output_size
			else:
				new_h, new_w = self.output_size, self.output_size*w/h
		else:
			new_h, new_w = self.output_size

		new_h, new_w = int(new_h), int(new_w)

		# resize the image to new_h x new_w and convert image from range [0,255] to [0,1]
		img = transform.resize(image, (new_h, new_w), mode='constant')
		lbl = transform.resize(label, (new_h, new_w), mode='constant', order=0, preserve_range=True)
		edge = transform.resize(edge, (new_h, new_w), mode='constant', order=0, preserve_range=True)

		return {'image': img, 'label': lbl, 'edge': edge}


class CenterCrop(object):

	def __init__(self, output_size):
		assert isinstance(output_size, (int, tuple))
		if isinstance(output_size, int):
			self.output_size = (output_size, output_size)
		else:
			assert len(output_size) == 2
			self.output_size = output_size

	def __call__(self, sample):
		image, label, edge = sample['image'], sample['label'], sample['edge']
		h, w = image.shape[:2]
		new_h, new_w = self.output_size
		assert((h >= new_h) and (w >= new_w))

		h_offset = int(math.floor((h - new_h)/2))
		w_offset = int(math.floor((w - new_w)/2))

		image = image[h_offset: h_offset + new_h, w_offset: w_offset + new_w]
		label = label[h_offset: h_offset + new_h, w_offset: w_offset + new_w]
		edge = edge[h_offset: h_offset + new_h, w_offset: w_offset + new_w]

		return {'image': img, 'label': lbl, 'edge': edge}


class RandomCrop(object):

	def __init__(self, output_size):
		assert isinstance(output_size, (int, tuple))
		if isinstance(output_size, int):
			self.output_size = (output_size, output_size)
		else:
			assert len(output_size) == 2
			self.output_size = output_size

	def __call__(self, sample):
		image, label, edge = sample['image'], sample['label'], sample['edge']
		h, w = image.shape[:2]
		new_h, new_w = self.output_size

		top = np.random.randint(0, h - new_h)
		left = np.random.randint(0, w - new_w)

		image = image[top: top + new_h, left: left + new_w]
		label = label[top: top + new_h, left: left + new_w]
		edge = edge[top: top + new_h, left: left + new_w]

		return {'image': img, 'label': lbl, 'edge': edge}


class ToTensor(object):
	"""Convert ndarrays in sample to Tensors."""

	def __call__(self, sample):

		image, label, edge = sample['image'], sample['label'], sample['edge']

		tmpImg = np.zeros((image.shape[0], image.shape[1], 3))
		tmpLbl = np.zeros(label.shape)
		tmpedge = np.zeros(edge.shape)

		image = image/np.max(image)
		if np.max(label) < 1e-6:
			label = label
		else:
			label = label/np.max(label)

		if np.max(edge) < 1e-6:
			edge = edge
		else:
			edge = edge/np.max(edge)

		if image.shape[2] == 1:
			tmpImg[:, :, 0] = (image[:, :, 0]-0.4669)/0.2437
			tmpImg[:, :, 1] = (image[:, :, 0]-0.4669)/0.2437
			tmpImg[:, :, 2] = (image[:, :, 0]-0.4669)/0.2437
		else:
			tmpImg[:, :, 0] = (image[:, :, 0]-0.4669)/0.2437
			tmpImg[:, :, 1] = (image[:, :, 1]-0.4669)/0.2437
			tmpImg[:, :, 2] = (image[:, :, 2]-0.4669)/0.2437

		tmpLbl[:, :, 0] = label[:, :, 0]
		tmpedge[:, :, 0] = edge[:, :, 0]

		tmpImg = tmpImg.transpose((2, 0, 1))
		tmpLbl = label.transpose((2, 0, 1))
		tmpedge = edge.transpose((2, 0, 1))

		return {'image': torch.from_numpy(tmpImg), 'label': torch.from_numpy(tmpLbl), 'edge': torch.from_numpy(tmpedge)}


class ToTensorLab(object):
	"""Convert ndarrays in sample to Tensors."""
	def __init__(self, flag=0):
		self.flag = flag

	def __call__(self, sample):

		image, label, edge = sample['image'], sample['label'], sample['edge']

		tmpLbl = np.zeros(label.shape)
		tmpedge = np.zeros(edge.shape)

		if np.max(label) < 1e-6:
			label = label
		else:
			label = label/np.max(label)
		if np.max(edge) < 1e-6:
			edge = edge
		else:
			edge = edge/np.max(edge)

		if self.flag == 2:
			tmpImg = np.zeros((image.shape[0], image.shape[1], 6))
			tmpImgt = np.zeros((image.shape[0], image.shape[1], 3))
			if image.shape[2] == 1:
				tmpImgt[:, :, 0] = image[:, :, 0]
				tmpImgt[:, :, 1] = image[:, :, 0]
				tmpImgt[:, :, 2] = image[:, :, 0]
			else:
				tmpImgt = image

			tmpImgtl = color.rgb2lab(tmpImgt)

			# nomalize image to range [0,1]
			tmpImg[:, :, 0] = (tmpImgt[:, :, 0]-np.min(tmpImgt[:, :, 0]))/(np.max(tmpImgt[:, :, 0])-np.min(tmpImgt[:, :, 0]))
			tmpImg[:, :, 1] = (tmpImgt[:, :, 1]-np.min(tmpImgt[:, :, 1]))/(np.max(tmpImgt[:, :, 1])-np.min(tmpImgt[:, :, 1]))
			tmpImg[:, :, 2] = (tmpImgt[:, :, 2]-np.min(tmpImgt[:, :, 2]))/(np.max(tmpImgt[:, :, 2])-np.min(tmpImgt[:, :, 2]))
			tmpImg[:, :, 3] = (tmpImgtl[:, :, 0]-np.min(tmpImgtl[:, :, 0]))/(np.max(tmpImgtl[:, :, 0])-np.min(tmpImgtl[:, :, 0]))
			tmpImg[:, :, 4] = (tmpImgtl[:, :, 1]-np.min(tmpImgtl[:, :, 1]))/(np.max(tmpImgtl[:, :, 1])-np.min(tmpImgtl[:, :, 1]))
			tmpImg[:, :, 5] = (tmpImgtl[:, :, 2]-np.min(tmpImgtl[:, :, 2]))/(np.max(tmpImgtl[:, :, 2])-np.min(tmpImgtl[:, :, 2]))

			# 标准�?			tmpImg[:, :, 0] = (tmpImg[:, :, 0]-np.mean(tmpImg[:, :, 0]))/np.std(tmpImg[:, :, 0])
			tmpImg[:, :, 1] = (tmpImg[:, :, 1]-np.mean(tmpImg[:, :, 1]))/np.std(tmpImg[:, :, 1])
			tmpImg[:, :, 2] = (tmpImg[:, :, 2]-np.mean(tmpImg[:, :, 2]))/np.std(tmpImg[:, :, 2])
			tmpImg[:, :, 3] = (tmpImg[:, :, 3]-np.mean(tmpImg[:, :, 3]))/np.std(tmpImg[:, :, 3])
			tmpImg[:, :, 4] = (tmpImg[:, :, 4]-np.mean(tmpImg[:, :, 4]))/np.std(tmpImg[:, :, 4])
			tmpImg[:, :, 5] = (tmpImg[:, :, 5]-np.mean(tmpImg[:, :, 5]))/np.std(tmpImg[:, :, 5])

		elif self.flag == 1:                                            # with Lab color
			tmpImg = np.zeros((image.shape[0], image.shape[1], 3))

			if image.shape[2] == 1:
				tmpImg[:, :, 0] = image[:, :, 0]
				tmpImg[:, :, 1] = image[:, :, 0]
				tmpImg[:, :, 2] = image[:, :, 0]
			else:
				tmpImg = image

			tmpImg = color.rgb2lab(tmpImg)

			# Normalize
			tmpImg[:, :, 0] = (tmpImg[:, :, 0]-np.min(tmpImg[:, :, 0]))/(np.max(tmpImg[:, :, 0])-np.min(tmpImg[:, :, 0]))
			tmpImg[:, :, 1] = (tmpImg[:, :, 1]-np.min(tmpImg[:, :, 1]))/(np.max(tmpImg[:, :, 1])-np.min(tmpImg[:, :, 1]))
			tmpImg[:, :, 2] = (tmpImg[:, :, 2]-np.min(tmpImg[:, :, 2]))/(np.max(tmpImg[:, :, 2])-np.min(tmpImg[:, :, 2]))
			# Standard
			tmpImg[:, :, 0] = (tmpImg[:, :, 0]-np.mean(tmpImg[:, :, 0]))/np.std(tmpImg[:, :, 0])
			tmpImg[:, :, 1] = (tmpImg[:, :, 1]-np.mean(tmpImg[:, :, 1]))/np.std(tmpImg[:, :, 1])
			tmpImg[:, :, 2] = (tmpImg[:, :, 2]-np.mean(tmpImg[:, :, 2]))/np.std(tmpImg[:, :, 2])

		else:                                    # with rgb color
			tmpImg = np.zeros((image.shape[0], image.shape[1], 3))
			image = image/np.max(image)
			if image.shape[2] == 1:
				tmpImg[:, :, 0] = (image[:, :, 0]-0.4669)/0.2437
				tmpImg[:, :, 1] = (image[:, :, 0]-0.4669)/0.2437
				tmpImg[:, :, 2] = (image[:, :, 0]-0.4669)/0.2437
			else:
				tmpImg[:, :, 0] = (image[:, :, 0]-0.4669)/0.2437
				tmpImg[:, :, 1] = (image[:, :, 1]-0.4669)/0.2437
				tmpImg[:, :, 2] = (image[:, :, 2]-0.4669)/0.2437

		tmpLbl[:, :, 0] = label[:, :, 0]
		tmpedge[:, :, 0] = edge[:, :, 0]

		# change the r,g,b to b,r,g from [0,255] to [0,1]
		tmpImg = tmpImg.transpose((2, 0, 1))
		tmpLbl = label.transpose((2, 0, 1))
		tmpedge = edge.transpose((2, 0, 1))

		return {'image': torch.from_numpy(tmpImg), 'label': torch.from_numpy(tmpLbl), 'edge': torch.from_numpy(tmpedge)}


class SalObjDataset(Dataset):
	def __init__(self, img_name_list, lbl_name_list, edge_name_list, transform=None):
		self.image_name_list = img_name_list
		self.label_name_list = lbl_name_list
		self.edge_name_list = edge_name_list
		self.transform = transform

	def __len__(self):
		return len(self.image_name_list)

	def __getitem__(self, idx):
		image = io.imread(self.image_name_list[idx])

		if 0 == len(self.label_name_list):
			label_3 = np.zeros(image.shape)
			edge_3 = np.zeros(image.shape)
		else:
			label_3 = io.imread(self.label_name_list[idx])
			edge_3 = io.imread(self.edge_name_list[idx])

		label = np.zeros(label_3.shape[0:2])
		edge = np.zeros(edge_3.shape[0:2])
		
		if 3 == len(label_3.shape):
			label = label_3[:, :, 0]
		elif 2 == len(label_3.shape):
			label = label_3
      
		if 3 == len(edge_3.shape):
			edge = edge_3[:, :, 0]
		elif 2 == len(edge_3.shape):
			edge = edge_3

		if 3 == len(image.shape) and 2 == len(label.shape):
			label = label[:, :, np.newaxis]
			edge = edge[:, :, np.newaxis]
		elif 2 == len(image.shape) and 2 == len(label.shape):
			image = image[:, :, np.newaxis]
			label = label[:, :, np.newaxis]
			edge = edge[:, :, np.newaxis]

		sample = {'image': image, 'label': label, 'edge': edge}

		if self.transform:
			sample = self.transform(sample)

		return sample
